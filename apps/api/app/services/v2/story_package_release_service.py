from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import sys
from typing import Any
from uuid import UUID, uuid4

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from apps.workers.jobs.story_package import build_story_package_artifacts
from app.schemas.v2.story_package import StoryPackageManifestV1
from app.schemas.v2.story_package_release import (
    StoryPackageBuildCommandV1,
    StoryPackageBuildV1,
    StoryPackageDraftIndexV1,
    StoryPackageDraftV1,
    StoryPackageHistoryV1,
    StoryPackageRecallCommandV1,
    StoryPackageReleaseCommandV1,
    StoryPackageReleaseV1,
    StoryPackageRollbackCommandV1,
)
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.object_storage_service import (
    ObjectStorageService,
    PlaceholderOssStorageService,
)
from app.services.v2.story_package_release_store import StoryPackageReleaseStore
from app.services.v2.story_package_service import DemoStoryPackageService, StoryPackageService


class StoryPackageReleaseNotFoundError(LookupError):
    """Raised when a package, build, or release record is missing."""


class StoryPackageReleaseValidationError(ValueError):
    """Raised when a release-loop command is invalid for the current state."""


def _isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _review_status_from_audit(audit_status: str) -> str:
    if audit_status == "approved":
        return "approved"

    if audit_status == "recalled":
        return "recalled"

    return "limited_release"


class StoryPackageReleaseService:
    def __init__(
        self,
        base_story_package_service: StoryPackageService,
        store: StoryPackageReleaseStore,
        storage_service: ObjectStorageService,
        clock: Callable[[], datetime],
    ):
        self.base_story_package_service = base_story_package_service
        self.store = store
        self.storage_service = storage_service
        self.clock = clock

    def list_drafts(self) -> StoryPackageDraftIndexV1:
        state = self._load_state()
        drafts = [self._build_draft_payload(draft, state) for draft in state["drafts"]]
        return StoryPackageDraftIndexV1(
            generated_at=self.clock(),
            drafts=drafts,
        )

    def get_history(self, package_id: UUID) -> StoryPackageHistoryV1:
        state = self._load_state()
        draft = self._find_draft(state, package_id)
        builds = self._list_builds_for_package(state, package_id)
        releases = self._list_releases_for_package(state, package_id)

        return StoryPackageHistoryV1(
            package_id=package_id,
            draft=self._build_draft_payload(draft, state),
            builds=[self._build_build_payload(item) for item in builds],
            releases=[self._build_release_payload(item) for item in releases],
            active_release_id=UUID(draft["active_release_id"]) if draft.get("active_release_id") else None,
            generated_at=self.clock(),
        )

    def resolve_story_package(self, package_id: UUID) -> StoryPackageManifestV1:
        state = self._load_state()
        draft = self._find_draft(state, package_id)
        return self._resolve_package_preview(draft, state)

    def build_package(
        self,
        package_id: UUID,
        command: StoryPackageBuildCommandV1,
    ) -> StoryPackageBuildV1:
        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._bootstrap_release_state(state)
            draft = self._find_draft(state, package_id)
            build_version = (
                max(
                    (item["build_version"] for item in state["builds"] if item["package_id"] == str(package_id)),
                    default=0,
                )
                + 1
            )
            package_payload = self._resolve_source_package(draft)
            built_package, artifact_plan = build_story_package_artifacts(
                package_payload,
                build_version=build_version,
                resolve_public_url=self.storage_service.get_public_url,
            )
            build_record = {
                "schema_version": "story-package-build.v1",
                "build_id": str(uuid4()),
                "draft_id": draft["draft_id"],
                "package_id": str(package_id),
                "build_version": build_version,
                "status": "succeeded",
                "build_reason": command.build_reason,
                "worker_job_id": f"story-package-build:{package_id}:v{build_version}",
                "manifest_object_key": artifact_plan.manifest_object_key,
                "artifact_root_object_key": artifact_plan.artifact_root_object_key,
                "requested_by": command.requested_by,
                "requested_at": command_time,
                "completed_at": command_time,
                "failure_message": None,
                "built_package": built_package,
            }
            state["builds"].append(build_record)
            draft["latest_build_id"] = build_record["build_id"]
            draft["workflow_state"] = "built"
            draft["updated_at"] = command_time
            draft["operator_notes"].append(
                f"Built version {build_version} for {command.build_reason} by {command.requested_by}."
            )
            return build_record

        return self._build_build_payload(self.store.update(mutate))

    def release_package(
        self,
        package_id: UUID,
        command: StoryPackageReleaseCommandV1,
    ) -> StoryPackageReleaseV1:
        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._bootstrap_release_state(state)
            draft = self._find_draft(state, package_id)
            build = self._find_build(state, command.build_id)
            audit = self._find_audit(state, draft["safety_audit_id"])

            if build["package_id"] != str(package_id):
                raise StoryPackageReleaseValidationError("Build does not belong to the requested package.")

            self._assert_release_allowed(audit)

            for release in state["releases"]:
                if release["package_id"] == str(package_id) and release["status"] == "active":
                    release["status"] = "superseded"

            release_version = (
                max(
                    (item["release_version"] for item in state["releases"] if item["package_id"] == str(package_id)),
                    default=0,
                )
                + 1
            )
            release_record = {
                "schema_version": "story-package-release.v1",
                "release_id": str(uuid4()),
                "package_id": str(package_id),
                "draft_id": draft["draft_id"],
                "build_id": build["build_id"],
                "release_version": release_version,
                "release_channel": command.release_channel,
                "status": "active",
                "runtime_lookup_key": f"/api/v2/story-packages/{package_id}",
                "requested_by": command.requested_by,
                "released_at": command_time,
                "notes": command.notes,
                "recalled_at": None,
                "rollback_of_release_id": None,
            }
            state["releases"].append(release_record)
            draft["active_release_id"] = release_record["release_id"]
            draft["workflow_state"] = "released"
            draft["updated_at"] = command_time
            draft["operator_notes"].append(
                f"Released build {build['build_version']} to {command.release_channel} by {command.requested_by}."
            )
            return release_record

        return self._build_release_payload(self.store.update(mutate))

    def recall_release(
        self,
        package_id: UUID,
        command: StoryPackageRecallCommandV1,
    ) -> StoryPackageReleaseV1:
        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._bootstrap_release_state(state)
            draft = self._find_draft(state, package_id)
            release = self._find_release(state, command.release_id)

            if release["package_id"] != str(package_id):
                raise StoryPackageReleaseValidationError("Release does not belong to the requested package.")

            if draft.get("active_release_id") != release["release_id"]:
                raise StoryPackageReleaseValidationError("Only the active release can be recalled.")

            release["status"] = "recalled"
            release["recalled_at"] = command_time
            release["notes"] = command.reason or release.get("notes")

            fallback_release = next(
                (
                    item
                    for item in self._list_releases_for_package(state, package_id)
                    if item["release_id"] != release["release_id"] and item["status"] != "recalled"
                ),
                None,
            )

            if fallback_release is not None:
                fallback_release["status"] = "active"
                draft["active_release_id"] = fallback_release["release_id"]
                draft["workflow_state"] = "released"
            else:
                draft["active_release_id"] = None
                draft["workflow_state"] = "recalled"

            draft["updated_at"] = command_time
            draft["operator_notes"].append(
                f"Recalled release {release['release_version']} by {command.requested_by}."
            )
            return release

        return self._build_release_payload(self.store.update(mutate))

    def rollback_release(
        self,
        package_id: UUID,
        command: StoryPackageRollbackCommandV1,
    ) -> StoryPackageReleaseV1:
        command_time = _isoformat(command.requested_at)

        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._bootstrap_release_state(state)
            draft = self._find_draft(state, package_id)
            target_release = self._find_release(state, command.target_release_id)
            audit = self._find_audit(state, draft["safety_audit_id"])

            if target_release["package_id"] != str(package_id):
                raise StoryPackageReleaseValidationError("Target release does not belong to the requested package.")

            if target_release["status"] == "recalled":
                raise StoryPackageReleaseValidationError("Recalled releases cannot be promoted through rollback.")

            self._assert_release_allowed(audit)

            for release in state["releases"]:
                if release["package_id"] == str(package_id) and release["status"] == "active":
                    release["status"] = "superseded"

            release_version = (
                max(
                    (item["release_version"] for item in state["releases"] if item["package_id"] == str(package_id)),
                    default=0,
                )
                + 1
            )
            release_record = {
                "schema_version": "story-package-release.v1",
                "release_id": str(uuid4()),
                "package_id": str(package_id),
                "draft_id": draft["draft_id"],
                "build_id": target_release["build_id"],
                "release_version": release_version,
                "release_channel": target_release["release_channel"],
                "status": "active",
                "runtime_lookup_key": f"/api/v2/story-packages/{package_id}",
                "requested_by": command.requested_by,
                "released_at": command_time,
                "notes": command.reason,
                "recalled_at": None,
                "rollback_of_release_id": target_release["release_id"],
            }
            state["releases"].append(release_record)
            draft["active_release_id"] = release_record["release_id"]
            draft["workflow_state"] = "released"
            draft["updated_at"] = command_time
            draft["operator_notes"].append(
                f"Rolled back to release {target_release['release_version']} by {command.requested_by}."
            )
            return release_record

        return self._build_release_payload(self.store.update(mutate))

    def _load_state(self) -> dict[str, Any]:
        def mutate(state: dict[str, Any]) -> dict[str, Any]:
            self._bootstrap_release_state(state)
            return state

        return self.store.update(mutate)

    def _bootstrap_release_state(self, state: dict[str, Any]) -> None:
        state.setdefault("drafts", [])
        state.setdefault("audits", [])
        state.setdefault("builds", [])
        state.setdefault("releases", [])

        for draft in state["drafts"]:
            package_id = draft["package_id"]
            if any(item["package_id"] == package_id for item in state["builds"]):
                continue

            built_package, artifact_plan = build_story_package_artifacts(
                self._resolve_source_package(draft),
                build_version=1,
                resolve_public_url=self.storage_service.get_public_url,
            )
            build_id = str(uuid4())
            release_id = str(uuid4())
            bootstrap_time = _isoformat(FIXTURE_TIMESTAMP)
            state["builds"].append(
                {
                    "schema_version": "story-package-build.v1",
                    "build_id": build_id,
                    "draft_id": draft["draft_id"],
                    "package_id": package_id,
                    "build_version": 1,
                    "status": "succeeded",
                    "build_reason": "bootstrap_release",
                    "worker_job_id": f"story-package-build:{package_id}:v1",
                    "manifest_object_key": artifact_plan.manifest_object_key,
                    "artifact_root_object_key": artifact_plan.artifact_root_object_key,
                    "requested_by": "bootstrap",
                    "requested_at": bootstrap_time,
                    "completed_at": bootstrap_time,
                    "failure_message": None,
                    "built_package": built_package,
                }
            )
            state["releases"].append(
                {
                    "schema_version": "story-package-release.v1",
                    "release_id": release_id,
                    "package_id": package_id,
                    "draft_id": draft["draft_id"],
                    "build_id": build_id,
                    "release_version": 1,
                    "release_channel": "pilot",
                    "status": "active",
                    "runtime_lookup_key": f"/api/v2/story-packages/{package_id}",
                    "requested_by": "bootstrap",
                    "released_at": bootstrap_time,
                    "notes": "Bootstrap release seeded from the V2 fixture package.",
                    "recalled_at": None,
                    "rollback_of_release_id": None,
                }
            )
            draft["latest_build_id"] = build_id
            draft["active_release_id"] = release_id
            draft["workflow_state"] = "released"
            draft["updated_at"] = bootstrap_time

    def _resolve_source_package(self, draft: dict[str, Any]) -> dict[str, Any]:
        preview_override = draft.get("package_preview_override")
        if preview_override:
            return deepcopy(preview_override)

        return self.base_story_package_service.get_story_package(
            UUID(draft["package_id"])
        ).model_dump(mode="json")

    def _resolve_package_preview(
        self,
        draft: dict[str, Any],
        state: dict[str, Any],
    ) -> StoryPackageManifestV1:
        audit = self._find_audit(state, draft["safety_audit_id"])
        active_release_id = draft.get("active_release_id")
        release_records = self._list_releases_for_package(
            state,
            UUID(draft["package_id"]),
        )

        if active_release_id:
            release = self._find_release(state, UUID(active_release_id))
            build = self._find_build(state, UUID(release["build_id"]))
            package_payload = deepcopy(build["built_package"])
            package_payload["release_channel"] = release["release_channel"]
            review_status = _review_status_from_audit(audit["audit_status"])
        elif release_records:
            release = release_records[0]
            build = self._find_build(state, UUID(release["build_id"]))
            package_payload = deepcopy(build["built_package"])
            package_payload["release_channel"] = release["release_channel"]
            review_status = (
                "recalled"
                if release["status"] == "recalled"
                else _review_status_from_audit(audit["audit_status"])
            )
        else:
            package_payload = self._resolve_source_package(draft)
            review_status = _review_status_from_audit(audit["audit_status"])

        package_payload["safety"]["review_status"] = review_status
        package_payload["safety"]["reviewed_at"] = audit.get("reviewed_at")
        package_payload["safety"]["review_policy_version"] = audit.get("policy_version")
        return StoryPackageManifestV1.model_validate(package_payload)

    def _build_draft_payload(
        self,
        draft: dict[str, Any],
        state: dict[str, Any],
    ) -> StoryPackageDraftV1:
        return StoryPackageDraftV1.model_validate(
            {
                "draft_id": draft["draft_id"],
                "package_id": draft["package_id"],
                "source_type": draft["source_type"],
                "workflow_state": draft["workflow_state"],
                "package_preview": self._resolve_package_preview(draft, state).model_dump(mode="json"),
                "safety_audit": self._find_audit(state, draft["safety_audit_id"]),
                "operator_notes": list(draft.get("operator_notes", [])),
                "latest_build_id": draft.get("latest_build_id"),
                "active_release_id": draft.get("active_release_id"),
                "created_at": draft["created_at"],
                "updated_at": draft["updated_at"],
            }
        )

    @staticmethod
    def _build_build_payload(build: dict[str, Any]) -> StoryPackageBuildV1:
        return StoryPackageBuildV1.model_validate(build)

    @staticmethod
    def _build_release_payload(release: dict[str, Any]) -> StoryPackageReleaseV1:
        return StoryPackageReleaseV1.model_validate(release)

    @staticmethod
    def _find_draft(state: dict[str, Any], package_id: UUID) -> dict[str, Any]:
        draft = next((item for item in state["drafts"] if item["package_id"] == str(package_id)), None)
        if draft is None:
            raise StoryPackageReleaseNotFoundError(f"Unknown package id: {package_id}")
        return draft

    @staticmethod
    def _find_build(state: dict[str, Any], build_id: UUID) -> dict[str, Any]:
        build = next((item for item in state["builds"] if item["build_id"] == str(build_id)), None)
        if build is None:
            raise StoryPackageReleaseNotFoundError(f"Unknown build id: {build_id}")
        return build

    @staticmethod
    def _find_release(state: dict[str, Any], release_id: UUID) -> dict[str, Any]:
        release = next((item for item in state["releases"] if item["release_id"] == str(release_id)), None)
        if release is None:
            raise StoryPackageReleaseNotFoundError(f"Unknown release id: {release_id}")
        return release

    @staticmethod
    def _assert_release_allowed(audit: dict[str, Any]) -> None:
        if audit["audit_status"] != "approved":
            raise StoryPackageReleaseValidationError(
                "Only packages with an approved safety audit can be released."
            )

        if audit.get("resolution", {}).get("action") != "release":
            raise StoryPackageReleaseValidationError(
                "Safety audit resolution must explicitly allow release."
            )

    @staticmethod
    def _find_audit(state: dict[str, Any], audit_id: str) -> dict[str, Any]:
        audit = next((item for item in state["audits"] if item["audit_id"] == audit_id), None)
        if audit is None:
            raise StoryPackageReleaseNotFoundError(f"Unknown audit id: {audit_id}")
        return audit

    @staticmethod
    def _list_builds_for_package(state: dict[str, Any], package_id: UUID) -> list[dict[str, Any]]:
        return sorted(
            [item for item in state["builds"] if item["package_id"] == str(package_id)],
            key=lambda current: current["build_version"],
            reverse=True,
        )

    @staticmethod
    def _list_releases_for_package(state: dict[str, Any], package_id: UUID) -> list[dict[str, Any]]:
        return sorted(
            [item for item in state["releases"] if item["package_id"] == str(package_id)],
            key=lambda current: current["release_version"],
            reverse=True,
        )


class ReleaseAwareStoryPackageService:
    def __init__(
        self,
        base_story_package_service: StoryPackageService,
        release_service: StoryPackageReleaseService,
    ):
        self.base_story_package_service = base_story_package_service
        self.release_service = release_service

    def get_story_package(self, package_id: UUID) -> StoryPackageManifestV1:
        return self.release_service.resolve_story_package(package_id)

    def list_story_packages(self, package_ids: list[UUID]) -> list[StoryPackageManifestV1]:
        return [self.get_story_package(package_id) for package_id in package_ids]


def create_release_story_package_services(
    clock: Callable[[], datetime] | None = None,
) -> tuple[ReleaseAwareStoryPackageService, StoryPackageReleaseService]:
    base_story_package_service = DemoStoryPackageService()
    release_service = StoryPackageReleaseService(
        base_story_package_service=base_story_package_service,
        store=StoryPackageReleaseStore(),
        storage_service=PlaceholderOssStorageService(),
        clock=clock or (lambda: FIXTURE_TIMESTAMP),
    )
    return ReleaseAwareStoryPackageService(base_story_package_service, release_service), release_service
