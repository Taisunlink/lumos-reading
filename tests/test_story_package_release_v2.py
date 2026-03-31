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


PACKAGE_ID = "33333333-3333-3333-3333-333333333333"


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


def build_request_time(step: int) -> str:
    return f"2026-03-31T10:0{step}:00Z"


def test_story_package_draft_index_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        "/api/v2/story-packages",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "story-package-draft-index.v1.schema.json")
    assert payload["schema_version"] == "story-package-draft-index.v1"
    assert len(payload["drafts"]) >= 3
    assert payload["drafts"][0]["package_preview"]["schema_version"] == "story-package.v1"


def test_story_package_build_release_and_runtime_lookup() -> None:
    client = TestClient(app)
    build_request = {
      "schema_version": "story-package-build-command.v1",
      "build_reason": "editorial_release",
      "requested_by": "studio.operator",
      "requested_at": build_request_time(1),
    }
    validate_payload(build_request, "story-package-build-command.v1.schema.json")

    build_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:build",
        headers={"host": "localhost"},
        json=build_request,
    )
    assert build_response.status_code == 200

    build_payload = build_response.json()
    validate_payload(build_payload, "story-package-build.v1.schema.json")
    assert build_payload["build_version"] == 2
    assert build_payload["manifest_object_key"].endswith("/build-2/manifest.json")

    release_request = {
      "schema_version": "story-package-release-command.v1",
      "build_id": build_payload["build_id"],
      "release_channel": "general",
      "requested_by": "studio.operator",
      "requested_at": build_request_time(2),
      "notes": "Promote for runtime validation.",
    }
    validate_payload(release_request, "story-package-release-command.v1.schema.json")

    release_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:release",
        headers={"host": "localhost"},
        json=release_request,
    )
    assert release_response.status_code == 200

    release_payload = release_response.json()
    validate_payload(release_payload, "story-package-release.v1.schema.json")
    assert release_payload["release_version"] == 2
    assert release_payload["release_channel"] == "general"
    assert release_payload["status"] == "active"

    runtime_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert runtime_response.status_code == 200

    runtime_payload = runtime_response.json()
    validate_payload(runtime_payload, "story-package.v1.schema.json")
    assert runtime_payload["release_channel"] == "general"
    assert "/build-2/" in runtime_payload["cover_image_url"]

    history_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}/history",
        headers={"host": "localhost"},
    )
    assert history_response.status_code == 200

    history_payload = history_response.json()
    validate_payload(history_payload, "story-package-history.v1.schema.json")
    assert history_payload["active_release_id"] == release_payload["release_id"]
    assert history_payload["builds"][0]["build_id"] == build_payload["build_id"]
    assert history_payload["releases"][0]["release_id"] == release_payload["release_id"]


def test_story_package_recall_and_rollback_preserve_lookup_semantics() -> None:
    client = TestClient(app)

    seed_history_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}/history",
        headers={"host": "localhost"},
    )
    assert seed_history_response.status_code == 200
    seed_history = seed_history_response.json()
    seed_release = next(
        item for item in seed_history["releases"] if item["release_version"] == 1
    )

    def build_package(step: int) -> dict:
        response = client.post(
            f"/api/v2/story-packages/{PACKAGE_ID}:build",
            headers={"host": "localhost"},
            json={
                "schema_version": "story-package-build-command.v1",
                "build_reason": f"operator-pass-{step}",
                "requested_by": "studio.operator",
                "requested_at": build_request_time(step),
            },
        )
        assert response.status_code == 200
        payload = response.json()
        validate_payload(payload, "story-package-build.v1.schema.json")
        return payload

    def release_build(step: int, build_id: str, release_channel: str) -> dict:
        response = client.post(
            f"/api/v2/story-packages/{PACKAGE_ID}:release",
            headers={"host": "localhost"},
            json={
                "schema_version": "story-package-release-command.v1",
                "build_id": build_id,
                "release_channel": release_channel,
                "requested_by": "studio.operator",
                "requested_at": build_request_time(step),
                "notes": f"Release step {step}",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        validate_payload(payload, "story-package-release.v1.schema.json")
        return payload

    general_build = build_package(1)
    general_release = release_build(2, general_build["build_id"], "general")
    experimental_build = build_package(3)
    experimental_release = release_build(4, experimental_build["build_id"], "experimental")

    runtime_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert runtime_response.status_code == 200
    runtime_payload = runtime_response.json()
    assert runtime_payload["release_channel"] == "experimental"
    assert "/build-3/" in runtime_payload["cover_image_url"]

    recall_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:recall",
        headers={"host": "localhost"},
        json={
            "schema_version": "story-package-recall-command.v1",
            "release_id": experimental_release["release_id"],
            "requested_by": "studio.operator",
            "requested_at": build_request_time(5),
            "reason": "Recall after final review.",
        },
    )
    assert recall_response.status_code == 200
    recall_payload = recall_response.json()
    validate_payload(recall_payload, "story-package-release.v1.schema.json")
    assert recall_payload["status"] == "recalled"

    fallback_runtime_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert fallback_runtime_response.status_code == 200
    fallback_runtime_payload = fallback_runtime_response.json()
    assert fallback_runtime_payload["release_channel"] == general_release["release_channel"]
    assert "/build-2/" in fallback_runtime_payload["cover_image_url"]

    rollback_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:rollback",
        headers={"host": "localhost"},
        json={
            "schema_version": "story-package-rollback-command.v1",
            "target_release_id": seed_release["release_id"],
            "requested_by": "studio.operator",
            "requested_at": build_request_time(6),
            "reason": "Rollback to bootstrap stable package.",
        },
    )
    assert rollback_response.status_code == 200
    rollback_payload = rollback_response.json()
    validate_payload(rollback_payload, "story-package-release.v1.schema.json")
    assert rollback_payload["rollback_of_release_id"] == seed_release["release_id"]

    rolled_back_runtime_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert rolled_back_runtime_response.status_code == 200
    rolled_back_runtime_payload = rolled_back_runtime_response.json()
    assert rolled_back_runtime_payload["release_channel"] == "pilot"
    assert "/build-1/" in rolled_back_runtime_payload["cover_image_url"]


def test_recalling_only_active_release_keeps_recalled_runtime_state() -> None:
    client = TestClient(app)

    seed_history_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}/history",
        headers={"host": "localhost"},
    )
    assert seed_history_response.status_code == 200
    seed_history = seed_history_response.json()
    seed_release = next(
        item for item in seed_history["releases"] if item["release_version"] == 1
    )

    recall_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:recall",
        headers={"host": "localhost"},
        json={
            "schema_version": "story-package-recall-command.v1",
            "release_id": seed_release["release_id"],
            "requested_by": "studio.operator",
            "requested_at": build_request_time(7),
            "reason": "Recall the only active release.",
        },
    )
    assert recall_response.status_code == 200
    recall_payload = recall_response.json()
    validate_payload(recall_payload, "story-package-release.v1.schema.json")
    assert recall_payload["status"] == "recalled"

    runtime_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert runtime_response.status_code == 200
    runtime_payload = runtime_response.json()
    validate_payload(runtime_payload, "story-package.v1.schema.json")
    assert runtime_payload["safety"]["review_status"] == "recalled"
    assert runtime_payload["release_channel"] == "pilot"
    assert "/build-1/" in runtime_payload["cover_image_url"]

    history_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}/history",
        headers={"host": "localhost"},
    )
    assert history_response.status_code == 200
    history_payload = history_response.json()
    validate_payload(history_payload, "story-package-history.v1.schema.json")
    assert history_payload["draft"]["workflow_state"] == "recalled"
    assert history_payload.get("active_release_id") is None


def test_cannot_rollback_a_recalled_release() -> None:
    client = TestClient(app)

    seed_history_response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}/history",
        headers={"host": "localhost"},
    )
    assert seed_history_response.status_code == 200
    seed_history = seed_history_response.json()
    seed_release = next(
        item for item in seed_history["releases"] if item["release_version"] == 1
    )

    recall_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:recall",
        headers={"host": "localhost"},
        json={
            "schema_version": "story-package-recall-command.v1",
            "release_id": seed_release["release_id"],
            "requested_by": "studio.operator",
            "requested_at": build_request_time(8),
            "reason": "Recall before rollback validation.",
        },
    )
    assert recall_response.status_code == 200

    rollback_response = client.post(
        f"/api/v2/story-packages/{PACKAGE_ID}:rollback",
        headers={"host": "localhost"},
        json={
            "schema_version": "story-package-rollback-command.v1",
            "target_release_id": seed_release["release_id"],
            "requested_by": "studio.operator",
            "requested_at": build_request_time(9),
            "reason": "This recalled release must stay blocked.",
        },
    )
    assert rollback_response.status_code == 400


def test_unknown_story_package_history_returns_404() -> None:
    client = TestClient(app)
    unknown_package_id = "aaaaaaaa-0000-1111-2222-bbbbbbbbbbbb"

    history_response = client.get(
        f"/api/v2/story-packages/{unknown_package_id}/history",
        headers={"host": "localhost"},
    )
    assert history_response.status_code == 404
