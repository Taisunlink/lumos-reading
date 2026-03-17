import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
SCHEMAS_DIR = ROOT_DIR / "packages" / "contracts" / "schemas"

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402


HOUSEHOLD_ID = "44444444-4444-4444-4444-444444444444"
PACKAGE_ID = "33333333-3333-3333-3333-333333333333"
CHILD_ID = "55555555-5555-5555-5555-555555555555"
SESSION_ID = "d1d3a8c0-05f3-45bd-9a56-72a911200099"


def load_schema(file_name: str) -> dict:
    with (SCHEMAS_DIR / file_name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_payload(payload: dict, schema_file_name: str) -> None:
    schema = load_schema(schema_file_name)
    Draft202012Validator(schema).validate(payload)


def test_contract_schema_files_exist() -> None:
    expected_files = [
        "caregiver-household.v1.schema.json",
        "caregiver-children.v1.schema.json",
        "caregiver-plan.v1.schema.json",
        "caregiver-progress.v1.schema.json",
        "caregiver-dashboard.v1.schema.json",
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
