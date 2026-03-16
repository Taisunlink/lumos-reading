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
        "safety-audit.v1.schema.json",
    ]

    for file_name in expected_files:
        assert (SCHEMAS_DIR / file_name).exists(), f"Missing schema file: {file_name}"


def test_caregiver_household_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(f"/api/v2/caregiver/households/{HOUSEHOLD_ID}", headers={"host": "localhost"})
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
