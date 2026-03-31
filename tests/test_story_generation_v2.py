import json
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
SCHEMAS_DIR = ROOT_DIR / "packages" / "contracts" / "schemas"

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402
from app.services.v2.story_package_release_store import (  # noqa: E402
    reset_story_package_release_state,
)


def load_schema(file_name: str) -> dict:
    with (SCHEMAS_DIR / file_name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_schema_registry() -> Registry:
    registry = Registry()

    for schema_path in SCHEMAS_DIR.glob("*.json"):
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        schema_id = schema.get("$id")
        if schema_id:
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))

    return registry


SCHEMA_REGISTRY = build_schema_registry()


@pytest.fixture(autouse=True)
def reset_release_store() -> None:
    reset_story_package_release_state()
    yield
    reset_story_package_release_state()


def validate_payload(payload: dict, schema_file_name: str) -> None:
    schema = load_schema(schema_file_name)
    Draft202012Validator(schema, registry=SCHEMA_REGISTRY).validate(payload)


def create_brief_for_test(client: TestClient, *, title: str = "Gentle Kite Letter") -> dict:
    payload = {
        "schema_version": "story-brief-command.v1",
        "title": title,
        "theme": "patience",
        "premise": "A child waits for a small message to return on the wind.",
        "language_mode": "en-US",
        "age_band": "4-6",
        "desired_page_count": 3,
        "source_outline": "Keep the mood calm and reviewable.",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:00:00Z",
    }
    validate_payload(payload, "story-brief-command.v1.schema.json")
    response = client.post(
        "/api/v2/story-briefs",
        headers={"host": "localhost"},
        json=payload,
    )
    assert response.status_code == 200
    resource = response.json()
    validate_payload(resource, "story-brief.v1.schema.json")
    return resource


def generate_draft_for_test(client: TestClient, brief_id: str) -> dict:
    payload = {
        "schema_version": "story-generation-job-command.v1",
        "job_type": "brief_to_draft",
        "provider_preference": "placeholder",
        "notes": "Contract test draft generation.",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:05:00Z",
    }
    validate_payload(payload, "story-generation-job-command.v1.schema.json")
    response = client.post(
        f"/api/v2/story-briefs/{brief_id}:generate-draft",
        headers={"host": "localhost"},
        json=payload,
    )
    assert response.status_code == 200
    resource = response.json()
    validate_payload(resource, "story-generation-job.v1.schema.json")
    return resource


def generate_media_for_test(client: TestClient, brief_id: str) -> dict:
    payload = {
        "schema_version": "story-generation-job-command.v1",
        "job_type": "draft_to_media",
        "provider_preference": "qwen",
        "notes": "Contract test media generation.",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:10:00Z",
    }
    validate_payload(payload, "story-generation-job-command.v1.schema.json")
    response = client.post(
        f"/api/v2/story-briefs/{brief_id}:generate-media",
        headers={"host": "localhost"},
        json=payload,
    )
    assert response.status_code == 200
    resource = response.json()
    validate_payload(resource, "story-generation-job.v1.schema.json")
    return resource


def test_seeded_story_brief_and_job_contracts_match_schema() -> None:
    client = TestClient(app)

    briefs_response = client.get(
        "/api/v2/story-briefs",
        headers={"host": "localhost"},
    )
    assert briefs_response.status_code == 200
    briefs_payload = briefs_response.json()
    validate_payload(briefs_payload, "story-brief-index.v1.schema.json")
    assert briefs_payload["briefs"][0]["status"] == "media_ready"

    jobs_response = client.get(
        "/api/v2/story-generation-jobs",
        headers={"host": "localhost"},
    )
    assert jobs_response.status_code == 200
    jobs_payload = jobs_response.json()
    validate_payload(jobs_payload, "story-generation-job-index.v1.schema.json")
    assert len(jobs_payload["jobs"]) >= 2
    assert any(job["selected_provider"] == "placeholder" for job in jobs_payload["jobs"])


def test_generate_draft_creates_reviewable_package_without_runtime_release() -> None:
    client = TestClient(app)
    brief = create_brief_for_test(client)
    job = generate_draft_for_test(client, brief["brief_id"])
    assert job["status"] == "succeeded"

    draft_index_response = client.get(
        "/api/v2/story-packages",
        headers={"host": "localhost"},
    )
    assert draft_index_response.status_code == 200
    draft_index_payload = draft_index_response.json()
    validate_payload(draft_index_payload, "story-package-draft-index.v1.schema.json")
    generated_draft = next(
        item for item in draft_index_payload["drafts"] if item["package_id"] == brief["package_id"]
    )
    assert generated_draft["source_type"] == "ai_generated"
    assert generated_draft["workflow_state"] == "draft"
    assert generated_draft.get("active_release_id") is None
    assert generated_draft["safety_audit"]["audit_status"] == "pending"

    history_response = client.get(
        f"/api/v2/story-packages/{brief['package_id']}/history",
        headers={"host": "localhost"},
    )
    assert history_response.status_code == 200
    history_payload = history_response.json()
    validate_payload(history_payload, "story-package-history.v1.schema.json")
    assert history_payload["builds"] == []
    assert history_payload["releases"] == []

    runtime_response = client.get(
        f"/api/v2/story-packages/{brief['package_id']}",
        headers={"host": "localhost"},
    )
    assert runtime_response.status_code == 404


def test_generate_media_records_provider_fallback_and_asset_keys() -> None:
    client = TestClient(app)
    brief = create_brief_for_test(client, title="Soft Lantern Return")
    generate_draft_for_test(client, brief["brief_id"])
    media_job = generate_media_for_test(client, brief["brief_id"])

    assert media_job["selected_provider"] == "placeholder"
    assert media_job["attempts"][0]["provider"] == "qwen"
    assert media_job["attempts"][0]["status"] == "failed"
    assert media_job["attempts"][-1]["provider"] == "placeholder"
    assert media_job["attempts"][-1]["status"] == "succeeded"
    assert len(media_job["generated_asset_keys"]) >= 7

    history_response = client.get(
        f"/api/v2/story-packages/{brief['package_id']}/history",
        headers={"host": "localhost"},
    )
    assert history_response.status_code == 200
    history_payload = history_response.json()
    validate_payload(history_payload, "story-package-history.v1.schema.json")
    assert "/story-packages/generated/" in history_payload["draft"]["package_preview"]["cover_image_url"]
    assert any(
        "placeholder" in note.lower() for note in history_payload["draft"]["operator_notes"]
    )


def test_review_build_release_generated_package_end_to_end() -> None:
    client = TestClient(app)
    brief = create_brief_for_test(client, title="Rain Shelf Promise")
    generate_draft_for_test(client, brief["brief_id"])
    generate_media_for_test(client, brief["brief_id"])

    review_payload = {
        "schema_version": "story-package-review-command.v1",
        "audit_status": "approved",
        "resolution_action": "release",
        "reviewer_type": "human",
        "reviewer_id": "studio.reviewer",
        "notes": "Approved for package build and runtime release.",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:15:00Z",
    }
    validate_payload(review_payload, "story-package-review-command.v1.schema.json")
    review_response = client.post(
        f"/api/v2/story-packages/{brief['package_id']}:review",
        headers={"host": "localhost"},
        json=review_payload,
    )
    assert review_response.status_code == 200
    review_resource = review_response.json()
    validate_payload(review_resource, "story-package-draft.v1.schema.json")
    assert review_resource["safety_audit"]["audit_status"] == "approved"
    assert review_resource["safety_audit"]["resolution"]["action"] == "release"

    build_payload = {
        "schema_version": "story-package-build-command.v1",
        "build_reason": "ai_release_validation",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:20:00Z",
    }
    validate_payload(build_payload, "story-package-build-command.v1.schema.json")
    build_response = client.post(
        f"/api/v2/story-packages/{brief['package_id']}:build",
        headers={"host": "localhost"},
        json=build_payload,
    )
    assert build_response.status_code == 200
    build_resource = build_response.json()
    validate_payload(build_resource, "story-package-build.v1.schema.json")
    assert build_resource["build_version"] == 1

    release_payload = {
        "schema_version": "story-package-release-command.v1",
        "build_id": build_resource["build_id"],
        "release_channel": "general",
        "requested_by": "studio.operator",
        "requested_at": "2026-03-31T11:25:00Z",
        "notes": "Release generated package after review approval.",
    }
    validate_payload(release_payload, "story-package-release-command.v1.schema.json")
    release_response = client.post(
        f"/api/v2/story-packages/{brief['package_id']}:release",
        headers={"host": "localhost"},
        json=release_payload,
    )
    assert release_response.status_code == 200
    release_resource = release_response.json()
    validate_payload(release_resource, "story-package-release.v1.schema.json")
    assert release_resource["release_version"] == 1

    runtime_response = client.get(
        f"/api/v2/story-packages/{brief['package_id']}",
        headers={"host": "localhost"},
    )
    assert runtime_response.status_code == 200
    runtime_payload = runtime_response.json()
    validate_payload(runtime_payload, "story-package.v1.schema.json")
    assert runtime_payload["release_channel"] == "general"
    assert "/build-1/" in runtime_payload["cover_image_url"]

    jobs_response = client.get(
        "/api/v2/story-generation-jobs",
        headers={"host": "localhost"},
    )
    assert jobs_response.status_code == 200
    jobs_payload = jobs_response.json()
    validate_payload(jobs_payload, "story-generation-job-index.v1.schema.json")
    matching_jobs = [
        item for item in jobs_payload["jobs"] if item["package_id"] == brief["package_id"]
    ]
    assert len(matching_jobs) == 2
