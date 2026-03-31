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
from app.services.v2.reading_event_store import (  # noqa: E402
    reset_ingested_reading_events,
)
from app.services.v2.child_service import reset_child_package_assignment_overrides  # noqa: E402
from app.services.v2.reading_event_store import reset_ingested_reading_events  # noqa: E402


HOUSEHOLD_ID = "44444444-4444-4444-4444-444444444444"
PACKAGE_ID = "33333333-3333-3333-3333-333333333333"
ENGLISH_PACKAGE_ID = "66666666-6666-6666-6666-666666666666"
SECOND_ENGLISH_PACKAGE_ID = "99999999-9999-9999-9999-999999999999"
CHILD_ID = "55555555-5555-5555-5555-555555555555"
SESSION_ID = "d1d3a8c0-05f3-45bd-9a56-72a911200099"


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
def reset_demo_runtime_state() -> None:
    reset_child_package_assignment_overrides()
    reset_ingested_reading_events()
    yield
    reset_child_package_assignment_overrides()
    reset_ingested_reading_events()


def validate_payload(payload: dict, schema_file_name: str) -> None:
    schema = load_schema(schema_file_name)
    Draft202012Validator(schema, registry=SCHEMA_REGISTRY).validate(payload)


def test_contract_schema_files_exist() -> None:
    expected_files = [
        "caregiver-assignment-command.v1.schema.json",
        "caregiver-assignment-response.v1.schema.json",
        "caregiver-household.v1.schema.json",
        "caregiver-children.v1.schema.json",
        "caregiver-plan.v1.schema.json",
        "caregiver-progress.v1.schema.json",
        "caregiver-dashboard.v1.schema.json",
        "child-home.v1.schema.json",
        "story-package.v1.schema.json",
        "reading-event.v1.schema.json",
        "reading-session-create.v2.schema.json",
        "reading-session-response.v2.schema.json",
        "reading-event-batch.v2.schema.json",
        "reading-event-ingested-response.v2.schema.json",
        "safety-audit.v1.schema.json",
    ]

    for file_name in expected_files:
        assert (SCHEMAS_DIR / file_name).exists(), f"Missing schema file: {file_name}"


def test_caregiver_household_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-household.v1.schema.json")
    assert payload["schema_version"] == "caregiver-household.v1"
    assert payload["featured_package"]["schema_version"] == "story-package.v1"


def test_caregiver_children_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-children.v1.schema.json")
    assert payload["schema_version"] == "caregiver-children.v1"
    assert payload["children"][0]["current_package"]["schema_version"] == "story-package.v1"


def test_caregiver_plan_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/plan",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-plan.v1.schema.json")
    assert payload["schema_version"] == "caregiver-plan.v1"
    assert payload["weekly_plan"][0]["package"]["schema_version"] == "story-package.v1"


def test_caregiver_progress_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/progress",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-progress.v1.schema.json")
    assert payload["schema_version"] == "caregiver-progress.v1"
    assert payload["recent_events"][0]["event"]["schema_version"] == "reading-event.v1"


def test_caregiver_progress_preserves_package_language_mode() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/progress",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-progress.v1.schema.json")

    events_by_package_id = {
        item["event"]["package_id"]: item["event"] for item in payload["recent_events"]
    }
    assert events_by_package_id[SECOND_ENGLISH_PACKAGE_ID]["language_mode"] == "en-US"
    assert events_by_package_id[ENGLISH_PACKAGE_ID]["language_mode"] == "en-US"


def build_assignment_payload(package_id: str) -> dict:
    return {
        "schema_version": "caregiver-assignment-command.v1",
        "household_id": HOUSEHOLD_ID,
        "child_id": CHILD_ID,
        "package_id": package_id,
        "source": "caregiver-web",
        "requested_at": "2026-03-31T09:30:00Z",
    }


def assign_package_for_test(client: TestClient, package_id: str) -> dict:
    request_payload = build_assignment_payload(package_id)
    validate_payload(request_payload, "caregiver-assignment-command.v1.schema.json")

    response = client.post(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children/{CHILD_ID}/assignment",
        headers={"host": "localhost"},
        json=request_payload,
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-assignment-response.v1.schema.json")
    return payload


def test_caregiver_dashboard_contract_still_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/dashboard",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "caregiver-dashboard.v1.schema.json")
    assert payload["schema_version"] == "caregiver-dashboard.v1"


def test_story_package_lookup_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/story-packages/{PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "story-package.v1.schema.json")
    assert payload["schema_version"] == "story-package.v1"
    assert payload["package_id"] == PACKAGE_ID
    assert len(payload["pages"]) >= 2


def test_child_home_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/child-home/{CHILD_ID}",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "child-home.v1.schema.json")
    assert payload["schema_version"] == "child-home.v1"
    assert payload["child_id"] == CHILD_ID
    assert payload["current_package_id"] == PACKAGE_ID
    assert len(payload["package_queue"]) >= 2


def test_caregiver_assignment_updates_children_and_child_home() -> None:
    client = TestClient(app)

    try:
        payload = assign_package_for_test(client, ENGLISH_PACKAGE_ID)
        assert payload["status"] == "accepted"
        assert payload["schema_version"] == "caregiver-assignment-response.v1"
        assert payload["current_package_id"] == ENGLISH_PACKAGE_ID
        assert payload["previous_package_id"] == PACKAGE_ID
        assert payload["current_package"]["language_mode"] == "en-US"
        assert payload["child_home"]["current_package_id"] == ENGLISH_PACKAGE_ID

        children_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children",
            headers={"host": "localhost"},
        )
        assert children_response.status_code == 200
        children_payload = children_response.json()
        validate_payload(children_payload, "caregiver-children.v1.schema.json")
        mina_assignment = next(
            child
            for child in children_payload["children"]
            if child["child_id"] == CHILD_ID
        )
        assert mina_assignment["current_package_id"] == ENGLISH_PACKAGE_ID
        assert mina_assignment["current_package"]["package_id"] == ENGLISH_PACKAGE_ID

        child_home_response = client.get(
            f"/api/v2/child-home/{CHILD_ID}",
            headers={"host": "localhost"},
        )
        assert child_home_response.status_code == 200
        child_home_payload = child_home_response.json()
        validate_payload(child_home_payload, "child-home.v1.schema.json")
        assert child_home_payload["current_package_id"] == ENGLISH_PACKAGE_ID
        assert child_home_payload["package_queue"][0]["package_id"] == ENGLISH_PACKAGE_ID
        assert child_home_payload["package_queue"][0]["language_mode"] == "en-US"
    finally:
        reset_payload = assign_package_for_test(client, PACKAGE_ID)
        assert reset_payload["current_package_id"] == PACKAGE_ID


def test_reading_session_contract_matches_schema() -> None:
    client = TestClient(app)
    request_payload = {
        "child_id": CHILD_ID,
        "package_id": PACKAGE_ID,
        "started_at": "2026-03-17T20:00:00Z",
        "mode": "read_to_me",
        "language_mode": "zh-CN",
        "assist_mode": ["read_aloud_sync", "focus_support"],
    }
    validate_payload(request_payload, "reading-session-create.v2.schema.json")

    response = client.post(
        "/api/v2/reading-sessions",
        headers={"host": "localhost"},
        json=request_payload,
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "reading-session-response.v2.schema.json")
    assert payload["status"] == "accepted"
    assert payload["child_id"] == CHILD_ID
    assert payload["package_id"] == PACKAGE_ID


def test_reading_event_batch_contract_matches_schema() -> None:
    client = TestClient(app)
    request_payload = {
        "events": [
            {
                "schema_version": "reading-event.v1",
                "event_id": "c1d3a8c0-05f3-45bd-9a56-72a911200101",
                "event_type": "session_started",
                "occurred_at": "2026-03-17T20:00:00Z",
                "session_id": SESSION_ID,
                "child_id": CHILD_ID,
                "package_id": PACKAGE_ID,
                "page_index": None,
                "platform": "ipadOS",
                "surface": "child-app",
                "app_version": "2.0.0",
                "language_mode": "zh-CN",
                "payload": {
                    "source": "contract-test",
                },
            },
            {
                "schema_version": "reading-event.v1",
                "event_id": "c1d3a8c0-05f3-45bd-9a56-72a911200102",
                "event_type": "page_viewed",
                "occurred_at": "2026-03-17T20:00:18Z",
                "session_id": SESSION_ID,
                "child_id": CHILD_ID,
                "package_id": PACKAGE_ID,
                "page_index": 0,
                "platform": "ipadOS",
                "surface": "child-app",
                "app_version": "2.0.0",
                "language_mode": "zh-CN",
                "payload": {
                    "dwell_ms": 18000,
                    "source": "contract-test",
                },
            },
        ]
    }
    validate_payload(request_payload, "reading-event-batch.v2.schema.json")

    response = client.post(
        "/api/v2/reading-events:batch",
        headers={"host": "localhost"},
        json=request_payload,
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "reading-event-ingested-response.v2.schema.json")
    assert payload["status"] == "accepted"
    assert payload["accepted_count"] == 2
    assert payload["session_ids"] == [SESSION_ID]


def test_reading_contracts_support_english_language_mode() -> None:
    client = TestClient(app)
    session_request_payload = {
        "child_id": CHILD_ID,
        "package_id": ENGLISH_PACKAGE_ID,
        "started_at": "2026-03-17T20:05:00Z",
        "mode": "read_to_me",
        "language_mode": "en-US",
        "assist_mode": ["read_aloud_sync", "focus_support"],
    }
    validate_payload(session_request_payload, "reading-session-create.v2.schema.json")

    session_response = client.post(
        "/api/v2/reading-sessions",
        headers={"host": "localhost"},
        json=session_request_payload,
    )
    assert session_response.status_code == 200
    validate_payload(
        session_response.json(),
        "reading-session-response.v2.schema.json",
    )

    event_request_payload = {
        "events": [
            {
                "schema_version": "reading-event.v1",
                "event_id": "c1d3a8c0-05f3-45bd-9a56-72a911200103",
                "event_type": "session_started",
                "occurred_at": "2026-03-17T20:05:00Z",
                "session_id": SESSION_ID,
                "child_id": CHILD_ID,
                "package_id": ENGLISH_PACKAGE_ID,
                "page_index": None,
                "platform": "ipadOS",
                "surface": "child-app",
                "app_version": "2.0.0",
                "language_mode": "en-US",
                "payload": {
                    "source": "contract-test",
                },
            }
        ]
    }
    validate_payload(event_request_payload, "reading-event-batch.v2.schema.json")

    event_response = client.post(
        "/api/v2/reading-events:batch",
        headers={"host": "localhost"},
        json=event_request_payload,
    )
    assert event_response.status_code == 200
    validate_payload(
        event_response.json(),
        "reading-event-ingested-response.v2.schema.json",
    )


def test_caregiver_progress_includes_newly_ingested_child_events() -> None:
    client = TestClient(app)
    reset_ingested_reading_events()

    try:
        request_payload = {
            "events": [
                {
                    "schema_version": "reading-event.v1",
                    "event_id": "c1d3a8c0-05f3-45bd-9a56-72a911200201",
                    "event_type": "session_completed",
                    "occurred_at": "2026-03-31T10:05:00Z",
                    "session_id": "d1d3a8c0-05f3-45bd-9a56-72a911200201",
                    "child_id": CHILD_ID,
                    "package_id": PACKAGE_ID,
                    "page_index": None,
                    "platform": "ipadOS",
                    "surface": "child-app",
                    "app_version": "2.0.0",
                    "language_mode": "zh-CN",
                    "payload": {
                        "dwell_ms": 240000,
                    },
                }
            ]
        }
        validate_payload(request_payload, "reading-event-batch.v2.schema.json")

        ingest_response = client.post(
            "/api/v2/reading-events:batch",
            headers={"host": "localhost"},
            json=request_payload,
        )
        assert ingest_response.status_code == 200

        progress_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/progress",
            headers={"host": "localhost"},
        )
        assert progress_response.status_code == 200

        progress_payload = progress_response.json()
        validate_payload(progress_payload, "caregiver-progress.v1.schema.json")
        matching_event = next(
            item
            for item in progress_payload["recent_events"]
            if item["event"]["event_id"] == "c1d3a8c0-05f3-45bd-9a56-72a911200201"
        )
        assert matching_event["child_name"] == "Mina"
        assert matching_event["package_title"] == "The Lantern Trail"
        assert matching_event["event"]["event_type"] == "session_completed"
        assert progress_payload["progress_metrics"]["completed_sessions"] >= 2
    finally:
        reset_ingested_reading_events()


def test_ingested_completed_session_appears_in_caregiver_progress() -> None:
    client = TestClient(app)
    event_request_payload = {
        "events": [
            {
                "schema_version": "reading-event.v1",
                "event_id": "c1d3a8c0-05f3-45bd-9a56-72a911200104",
                "event_type": "session_completed",
                "occurred_at": "2026-03-31T10:15:00Z",
                "session_id": "d1d3a8c0-05f3-45bd-9a56-72a911200104",
                "child_id": CHILD_ID,
                "package_id": ENGLISH_PACKAGE_ID,
                "page_index": None,
                "platform": "ipadOS",
                "surface": "child-app",
                "app_version": "2.0.0",
                "language_mode": "en-US",
                "payload": {
                    "dwell_ms": 420000,
                    "source": "phase-2-contract-test",
                },
            }
        ]
    }
    validate_payload(event_request_payload, "reading-event-batch.v2.schema.json")

    ingest_response = client.post(
        "/api/v2/reading-events:batch",
        headers={"host": "localhost"},
        json=event_request_payload,
    )
    assert ingest_response.status_code == 200
    validate_payload(
        ingest_response.json(),
        "reading-event-ingested-response.v2.schema.json",
    )

    progress_response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/progress",
        headers={"host": "localhost"},
    )
    assert progress_response.status_code == 200

    progress_payload = progress_response.json()
    validate_payload(progress_payload, "caregiver-progress.v1.schema.json")
    assert (
        progress_payload["recent_events"][0]["event"]["event_id"]
        == "c1d3a8c0-05f3-45bd-9a56-72a911200104"
    )
    assert progress_payload["recent_events"][0]["event"]["package_id"] == ENGLISH_PACKAGE_ID
    assert progress_payload["recent_events"][0]["event"]["language_mode"] == "en-US"
    assert progress_payload["progress_metrics"]["completed_sessions"] == 2
