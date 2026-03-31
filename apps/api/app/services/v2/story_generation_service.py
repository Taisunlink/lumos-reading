from collections.abc import Callable
from datetime import datetime
from pathlib import Path
import sys
from typing import Any
from uuid import UUID, uuid4

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from apps.workers.jobs.story_generation import (  # noqa: E402
    build_story_package_draft_from_brief,
    generate_story_package_media,
)
from app.schemas.v2.story_generation import (  # noqa: E402
    StoryBriefCommandV1,
    StoryBriefIndexV1,
    StoryBriefV1,
    StoryGenerationJobCommandV1,
    StoryGenerationJobIndexV1,
    StoryGenerationJobV1,
)
from app.services.v2.object_storage_service import (  # noqa: E402
    ObjectStorageService,
    PlaceholderOssStorageService,
)
from app.services.v2.story_package_release_store import StoryPackageReleaseStore  # noqa: E402


class StoryGenerationNotFoundError(LookupError):
    """Raised when a brief or draft cannot be resolved."""


class StoryGenerationValidationError(ValueError):
    """Raised when a generation command is invalid for the current state."""


def _isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


class StoryGenerationService:
    def __init__(
        self,
        store: StoryPackageReleaseStore,
        storage_service: ObjectStorageService,
        clock: Callable[[], datetime],
    ):
        self.store = store
        self.storage_service = storage_service
        self.clock = clock

    def list_briefs(self) -> StoryBriefIndexV1:
        state = self._load_state()
        return StoryBriefIndexV1(
            generated_at=self.clock(),
            briefs=[StoryBriefV1.model_validate(brief) for brief in state["briefs"]],
        )

    def create_brief(self, command: StoryBriefCommandV1) -> StoryBriefV1:
        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._ensure_generation_state(state)
            brief_record = {
                "schema_version": "story-brief.v1",
                "brief_id": str(uuid4()),
                "package_id": str(uuid4()),
                "title": command.title,
                "theme": command.theme,
                "premise": command.premise,
                "language_mode": command.language_mode,
                "age_band": command.age_band,
                "desired_page_count": command.desired_page_count,
                "status": "draft_requested",
                "source_outline": command.source_outline,
                "latest_job_id": None,
                "latest_failure_reason": None,
                "created_at": command_time,
                "updated_at": command_time,
            }
            state["briefs"].append(brief_record)
            return brief_record

        return StoryBriefV1.model_validate(self.store.update(mutate))

    def list_jobs(self) -> StoryGenerationJobIndexV1:
        state = self._load_state()
        jobs = sorted(
            state["generation_jobs"],
            key=lambda current: current["requested_at"],
            reverse=True,
        )
        return StoryGenerationJobIndexV1(
            generated_at=self.clock(),
            jobs=[StoryGenerationJobV1.model_validate(job) for job in jobs],
        )

    def generate_draft(
        self,
        brief_id: UUID,
        command: StoryGenerationJobCommandV1,
    ) -> StoryGenerationJobV1:
        if command.job_type != "brief_to_draft":
            raise StoryGenerationValidationError("Draft generation requires job_type=brief_to_draft.")

        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._ensure_generation_state(state)
            brief = self._find_brief(state, brief_id)
            package_id = brief["package_id"]
            self._assert_package_has_no_release_history(state, package_id)
            draft_result = build_story_package_draft_from_brief(brief, package_id)
            existing_draft = self._find_draft_for_package(state, package_id, required=False)
            audit_id = (
                existing_draft["safety_audit_id"]
                if existing_draft is not None
                else str(uuid4())
            )
            audit_record = {
                "schema_version": "safety-audit.v1",
                "audit_id": audit_id,
                "target_type": "story_package",
                "target_id": package_id,
                "audit_source": "pre_release",
                "audit_status": "pending",
                "severity": "medium",
                "policy_version": "2026.04-ai-draft",
                "findings": [
                    {
                        "code": "human-review-required",
                        "title": "Human review required",
                        "description": "AI-generated content must be reviewed before build and release.",
                        "severity": "medium",
                        "page_index": None,
                        "action_required": True,
                    }
                ],
                "reviewer": {
                    "reviewer_type": "system",
                    "reviewer_id": "ai.supply-chain",
                },
                "created_at": command_time,
                "reviewed_at": None,
                "resolution": {
                    "action": "revise",
                    "notes": "Awaiting editor review after draft generation.",
                    "resolved_at": None,
                },
            }
            self._upsert_audit(state, audit_record)

            draft_record = {
                "schema_version": "story-package-draft.v1",
                "draft_id": existing_draft["draft_id"] if existing_draft is not None else str(uuid4()),
                "package_id": package_id,
                "source_type": "ai_generated",
                "workflow_state": "draft",
                "safety_audit_id": audit_id,
                "operator_notes": [
                    *draft_result.operator_notes,
                    f"Draft generation requested by {command.requested_by}.",
                ],
                "latest_build_id": None,
                "active_release_id": None,
                "package_preview_override": draft_result.package_preview,
                "created_at": existing_draft["created_at"] if existing_draft is not None else command_time,
                "updated_at": command_time,
            }
            self._upsert_draft(state, draft_record)

            job_record = {
                "schema_version": "story-generation-job.v1",
                "job_id": str(uuid4()),
                "brief_id": str(brief_id),
                "package_id": package_id,
                "job_type": "brief_to_draft",
                "status": "succeeded",
                "selected_provider": "placeholder",
                "attempts": [
                    {
                        "provider": "placeholder",
                        "status": "succeeded",
                        "reason": "deterministic_draft_assembly",
                    }
                ],
                "generated_asset_keys": [],
                "requested_by": command.requested_by,
                "requested_at": command_time,
                "completed_at": command_time,
                "failure_reason": None,
                "notes": command.notes,
            }
            state["generation_jobs"].append(job_record)
            brief["status"] = "draft_ready"
            brief["latest_job_id"] = job_record["job_id"]
            brief["latest_failure_reason"] = None
            brief["updated_at"] = command_time
            return job_record

        return StoryGenerationJobV1.model_validate(self.store.update(mutate))

    def generate_media(
        self,
        brief_id: UUID,
        command: StoryGenerationJobCommandV1,
    ) -> StoryGenerationJobV1:
        if command.job_type != "draft_to_media":
            raise StoryGenerationValidationError("Media generation requires job_type=draft_to_media.")

        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._ensure_generation_state(state)
            brief = self._find_brief(state, brief_id)
            draft = self._find_draft_for_package(state, brief["package_id"])
            package_preview = draft.get("package_preview_override")

            if not package_preview:
                raise StoryGenerationValidationError(
                    "Draft generation must complete before media generation can start."
                )

            media_result = generate_story_package_media(
                package_preview,
                command.provider_preference,
                self.storage_service.get_public_url,
            )
            draft["package_preview_override"] = media_result.package_preview
            draft["updated_at"] = command_time
            draft["operator_notes"].append(
                f"Media generation completed with {media_result.selected_provider} for {brief['title']}."
            )
            failed_attempts = [
                attempt["provider"]
                for attempt in media_result.attempts
                if attempt["status"] == "failed"
            ]
            if failed_attempts:
                draft["operator_notes"].append(
                    "Provider fallback triggered after unavailable credentials: "
                    + ", ".join(failed_attempts)
                    + "."
                )

            job_record = {
                "schema_version": "story-generation-job.v1",
                "job_id": str(uuid4()),
                "brief_id": str(brief_id),
                "package_id": brief["package_id"],
                "job_type": "draft_to_media",
                "status": "succeeded",
                "selected_provider": media_result.selected_provider,
                "attempts": media_result.attempts,
                "generated_asset_keys": media_result.generated_asset_keys,
                "requested_by": command.requested_by,
                "requested_at": command_time,
                "completed_at": command_time,
                "failure_reason": None,
                "notes": command.notes,
            }
            state["generation_jobs"].append(job_record)
            brief["status"] = "media_ready"
            brief["latest_job_id"] = job_record["job_id"]
            brief["latest_failure_reason"] = None
            brief["updated_at"] = command_time
            return job_record

        return StoryGenerationJobV1.model_validate(self.store.update(mutate))

    def _load_state(self) -> dict[str, Any]:
        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._ensure_generation_state(state)
            return state

        return self.store.update(mutate)

    @staticmethod
    def _ensure_generation_state(state: dict[str, Any]) -> None:
        state.setdefault("briefs", [])
        state.setdefault("generation_jobs", [])
        state.setdefault("drafts", [])
        state.setdefault("audits", [])
        state.setdefault("builds", [])
        state.setdefault("releases", [])

    @staticmethod
    def _find_brief(state: dict[str, Any], brief_id: UUID) -> dict[str, Any]:
        brief = next((item for item in state["briefs"] if item["brief_id"] == str(brief_id)), None)
        if brief is None:
            raise StoryGenerationNotFoundError(f"Unknown brief id: {brief_id}")
        return brief

    @staticmethod
    def _find_draft_for_package(
        state: dict[str, Any],
        package_id: str,
        *,
        required: bool = True,
    ) -> dict[str, Any] | None:
        draft = next((item for item in state["drafts"] if item["package_id"] == package_id), None)
        if draft is None and required:
            raise StoryGenerationNotFoundError(f"Unknown draft package id: {package_id}")
        return draft

    @staticmethod
    def _upsert_draft(state: dict[str, Any], draft_record: dict[str, Any]) -> None:
        existing_index = next(
            (index for index, item in enumerate(state["drafts"]) if item["package_id"] == draft_record["package_id"]),
            None,
        )
        if existing_index is None:
            state["drafts"].append(draft_record)
            return
        state["drafts"][existing_index] = draft_record

    @staticmethod
    def _upsert_audit(state: dict[str, Any], audit_record: dict[str, Any]) -> None:
        existing_index = next(
            (index for index, item in enumerate(state["audits"]) if item["audit_id"] == audit_record["audit_id"]),
            None,
        )
        if existing_index is None:
            state["audits"].append(audit_record)
            return
        state["audits"][existing_index] = audit_record

    @staticmethod
    def _assert_package_has_no_release_history(state: dict[str, Any], package_id: str) -> None:
        if any(item["package_id"] == package_id for item in state["builds"]):
            raise StoryGenerationValidationError(
                "Draft generation is locked after package build history exists."
            )

        if any(item["package_id"] == package_id for item in state["releases"]):
            raise StoryGenerationValidationError(
                "Draft generation is locked after package release history exists."
            )


def create_story_generation_service(
    clock: Callable[[], datetime],
) -> StoryGenerationService:
    return StoryGenerationService(
        store=StoryPackageReleaseStore(),
        storage_service=PlaceholderOssStorageService(),
        clock=clock,
    )
