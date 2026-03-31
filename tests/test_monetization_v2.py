import json
import os
import sys
from pathlib import Path
from uuid import UUID

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
from app.services.v2.child_service import reset_child_package_assignment_overrides  # noqa: E402
from app.services.v2.fixtures import (  # noqa: E402
    DEMO_HOUSEHOLD_ID,
    HOUSEHOLD_ENTITLEMENT_FIXTURES,
    HouseholdEntitlementFixture,
    PackageAccessFixture,
)
from app.services.v2.package_access_store import reset_package_access_events  # noqa: E402
from app.services.v2.reading_event_store import reset_ingested_reading_events  # noqa: E402
from app.services.v2.story_package_release_store import reset_story_package_release_state  # noqa: E402


HOUSEHOLD_ID = "44444444-4444-4444-4444-444444444444"
CHILD_ID = "55555555-5555-5555-5555-555555555555"
ACCESSIBLE_PACKAGE_ID = "66666666-6666-6666-6666-666666666666"
LOCKED_PACKAGE_ID = "99999999-9999-9999-9999-999999999999"
DEFAULT_PACKAGE_ID = "33333333-3333-3333-3333-333333333333"


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
def reset_demo_state() -> None:
    reset_child_package_assignment_overrides()
    reset_package_access_events()
    reset_ingested_reading_events()
    reset_story_package_release_state()
    yield
    reset_child_package_assignment_overrides()
    reset_package_access_events()
    reset_ingested_reading_events()
    reset_story_package_release_state()


def validate_payload(payload: dict, schema_file_name: str) -> None:
    schema = load_schema(schema_file_name)
    Draft202012Validator(schema, registry=SCHEMA_REGISTRY).validate(payload)


def build_assignment_payload(package_id: str) -> dict:
    return {
        "schema_version": "caregiver-assignment-command.v1",
        "household_id": HOUSEHOLD_ID,
        "child_id": CHILD_ID,
        "package_id": package_id,
        "source": "caregiver-web",
        "requested_at": "2026-03-31T12:00:00Z",
    }


def override_household_entitlement(
    *,
    subscription_status: str,
    access_state: str,
    package_access: tuple[PackageAccessFixture, ...],
) -> HouseholdEntitlementFixture:
    original_fixture = HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID]
    HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID] = HouseholdEntitlementFixture(
        subscription_status=subscription_status,
        access_state=access_state,
        plan_name=original_fixture.plan_name,
        billing_interval=original_fixture.billing_interval,
        trial_ends_at=original_fixture.trial_ends_at,
        renews_at=original_fixture.renews_at,
        package_access=package_access,
    )
    return original_fixture


def test_household_entitlement_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/entitlement",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "household-entitlement.v1.schema.json")
    assert payload["schema_version"] == "household-entitlement.v1"
    assert payload["subscription_status"] == "trial_active"
    assert payload["access_state"] == "trial"
    assert payload["entitled_package_count"] == 2
    assert payload["locked_package_count"] == 1

    package_access_by_id = {
        item["package_id"]: item for item in payload["package_access"]
    }
    assert package_access_by_id[DEFAULT_PACKAGE_ID]["access_state"] == "entitled"
    assert package_access_by_id[ACCESSIBLE_PACKAGE_ID]["access_state"] == "entitled"
    assert package_access_by_id[LOCKED_PACKAGE_ID]["access_state"] == "locked"


def test_weekly_value_report_contract_matches_schema() -> None:
    client = TestClient(app)
    response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/weekly-value",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "weekly-value-report.v1.schema.json")
    assert payload["schema_version"] == "weekly-value-report.v1"
    assert payload["completed_sessions"] == 1
    assert payload["total_reading_minutes"] == 7
    assert payload["distinct_packages_completed"] == 1
    assert payload["reread_sessions"] == 0
    assert payload["value_score"] == 47
    assert len(payload["highlights"]) >= 1


def test_caregiver_assignment_blocks_locked_package_and_preserves_state() -> None:
    client = TestClient(app)
    request_payload = build_assignment_payload(LOCKED_PACKAGE_ID)
    validate_payload(request_payload, "caregiver-assignment-command.v1.schema.json")

    response = client.post(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children/{CHILD_ID}/assignment",
        headers={"host": "localhost"},
        json=request_payload,
    )
    assert response.status_code == 400

    children_response = client.get(
        f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children",
        headers={"host": "localhost"},
    )
    assert children_response.status_code == 200
    children_payload = children_response.json()
    validate_payload(children_payload, "caregiver-children.v1.schema.json")
    mina_assignment = next(
        child for child in children_payload["children"] if child["child_id"] == CHILD_ID
    )
    assert mina_assignment["current_package_id"] == DEFAULT_PACKAGE_ID

    child_home_response = client.get(
        f"/api/v2/child-home/{CHILD_ID}",
        headers={"host": "localhost"},
    )
    assert child_home_response.status_code == 200
    child_home_payload = child_home_response.json()
    validate_payload(child_home_payload, "child-home.v1.schema.json")
    assert child_home_payload["current_package_id"] == DEFAULT_PACKAGE_ID

    ops_response = client.get(
        "/api/v2/ops/metrics",
        headers={"host": "localhost"},
    )
    assert ops_response.status_code == 200
    ops_payload = ops_response.json()
    validate_payload(ops_payload, "ops-metrics-snapshot.v1.schema.json")
    assert ops_payload["blocked_package_requests"] == 1
    assert ops_payload["entitled_package_deliveries"] == 0


def test_child_home_queue_excludes_locked_package_and_scoped_delivery_enforces_entitlement() -> None:
    client = TestClient(app)

    child_home_response = client.get(
        f"/api/v2/child-home/{CHILD_ID}",
        headers={"host": "localhost"},
    )
    assert child_home_response.status_code == 200
    child_home_payload = child_home_response.json()
    validate_payload(child_home_payload, "child-home.v1.schema.json")
    queue_ids = [item["package_id"] for item in child_home_payload["package_queue"]]
    assert LOCKED_PACKAGE_ID not in queue_ids
    assert queue_ids == [DEFAULT_PACKAGE_ID, ACCESSIBLE_PACKAGE_ID]

    entitled_response = client.get(
        f"/api/v2/child-home/{CHILD_ID}/packages/{ACCESSIBLE_PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert entitled_response.status_code == 200
    entitled_payload = entitled_response.json()
    validate_payload(entitled_payload, "story-package.v1.schema.json")
    assert entitled_payload["package_id"] == ACCESSIBLE_PACKAGE_ID

    blocked_response = client.get(
        f"/api/v2/child-home/{CHILD_ID}/packages/{LOCKED_PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    assert blocked_response.status_code == 403

    ops_response = client.get(
        "/api/v2/ops/metrics",
        headers={"host": "localhost"},
    )
    assert ops_response.status_code == 200
    ops_payload = ops_response.json()
    validate_payload(ops_payload, "ops-metrics-snapshot.v1.schema.json")
    assert ops_payload["entitled_package_deliveries"] == 1
    assert ops_payload["blocked_package_requests"] == 1


def test_ops_metrics_snapshot_matches_schema_and_value_baseline() -> None:
    client = TestClient(app)

    client.get(
        f"/api/v2/child-home/{CHILD_ID}/packages/{ACCESSIBLE_PACKAGE_ID}",
        headers={"host": "localhost"},
    )
    client.get(
        f"/api/v2/child-home/{CHILD_ID}/packages/{LOCKED_PACKAGE_ID}",
        headers={"host": "localhost"},
    )

    response = client.get(
        "/api/v2/ops/metrics",
        headers={"host": "localhost"},
    )
    assert response.status_code == 200

    payload = response.json()
    validate_payload(payload, "ops-metrics-snapshot.v1.schema.json")
    assert payload["schema_version"] == "ops-metrics-snapshot.v1"
    assert payload["households_in_scope"] == 1
    assert payload["households_in_trial"] == 1
    assert payload["households_with_paid_access"] == 0
    assert payload["entitled_package_deliveries"] == 1
    assert payload["blocked_package_requests"] == 1
    assert payload["completed_sessions"] == 1
    assert payload["reuse_signals"] == 1
    assert payload["average_weekly_value_score"] == 47


def test_entitlement_loss_hides_previous_current_and_featured_package_across_read_models() -> None:
    client = TestClient(app)
    current_fixture = HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID]
    original_fixture = override_household_entitlement(
        subscription_status="trial_active",
        access_state="trial",
        package_access=(
            PackageAccessFixture(
                package_id=UUID(DEFAULT_PACKAGE_ID),
                access_state="locked",
                entitlement_source="subscription",
                reason="Trial catalog changed and this package is no longer unlocked.",
            ),
            *tuple(
                item
                for item in current_fixture.package_access
                if item.package_id != UUID(DEFAULT_PACKAGE_ID)
            ),
        ),
    )

    try:
        child_home_response = client.get(
            f"/api/v2/child-home/{CHILD_ID}",
            headers={"host": "localhost"},
        )
        assert child_home_response.status_code == 200
        child_home_payload = child_home_response.json()
        assert child_home_payload["current_package_id"] == ACCESSIBLE_PACKAGE_ID
        assert child_home_payload["featured_package_id"] == ACCESSIBLE_PACKAGE_ID
        assert [item["package_id"] for item in child_home_payload["package_queue"]] == [
            ACCESSIBLE_PACKAGE_ID
        ]

        children_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children",
            headers={"host": "localhost"},
        )
        assert children_response.status_code == 200
        children_payload = children_response.json()
        mina_assignment = next(
            child for child in children_payload["children"] if child["child_id"] == CHILD_ID
        )
        assert mina_assignment["current_package_id"] == ACCESSIBLE_PACKAGE_ID
        assert mina_assignment["current_package"]["package_id"] == ACCESSIBLE_PACKAGE_ID

        household_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}",
            headers={"host": "localhost"},
        )
        assert household_response.status_code == 200
        household_payload = household_response.json()
        assert household_payload["featured_package_id"] == ACCESSIBLE_PACKAGE_ID
        assert household_payload["featured_package"]["package_id"] == ACCESSIBLE_PACKAGE_ID
        assert [item["package_id"] for item in household_payload["package_queue"]] == [
            ACCESSIBLE_PACKAGE_ID
        ]

        dashboard_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/dashboard",
            headers={"host": "localhost"},
        )
        assert dashboard_response.status_code == 200
        dashboard_payload = dashboard_response.json()
        assert dashboard_payload["featured_package_id"] == ACCESSIBLE_PACKAGE_ID
        mina_summary = next(
            child for child in dashboard_payload["children"] if child["child_id"] == CHILD_ID
        )
        assert mina_summary["current_package_id"] == ACCESSIBLE_PACKAGE_ID
        assert [item["package_id"] for item in dashboard_payload["package_queue"]] == [
            ACCESSIBLE_PACKAGE_ID
        ]
        assert [item["package_id"] for item in dashboard_payload["weekly_plan"]] == [
            ACCESSIBLE_PACKAGE_ID,
            ACCESSIBLE_PACKAGE_ID,
        ]
    finally:
        HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID] = original_fixture


def test_zero_entitlement_household_returns_access_lost_without_crashing_read_surfaces() -> None:
    client = TestClient(app)
    original_fixture = override_household_entitlement(
        subscription_status="expired",
        access_state="expired",
        package_access=(
            PackageAccessFixture(
                package_id=UUID(DEFAULT_PACKAGE_ID),
                access_state="locked",
                entitlement_source="subscription",
                reason="Subscription expired and the starter package is no longer available.",
            ),
            PackageAccessFixture(
                package_id=UUID(ACCESSIBLE_PACKAGE_ID),
                access_state="locked",
                entitlement_source="subscription",
                reason="Subscription expired and the trial package is no longer available.",
            ),
            PackageAccessFixture(
                package_id=UUID(LOCKED_PACKAGE_ID),
                access_state="locked",
                entitlement_source="subscription",
                reason="Subscription expired and the premium package remains locked.",
            ),
        ),
    )

    try:
        entitlement_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/entitlement",
            headers={"host": "localhost"},
        )
        assert entitlement_response.status_code == 200
        entitlement_payload = entitlement_response.json()
        validate_payload(entitlement_payload, "household-entitlement.v1.schema.json")
        assert entitlement_payload["subscription_status"] == "expired"
        assert entitlement_payload["access_state"] == "expired"
        assert entitlement_payload["entitled_package_count"] == 0
        assert entitlement_payload["locked_package_count"] == 3

        child_home_response = client.get(
            f"/api/v2/child-home/{CHILD_ID}",
            headers={"host": "localhost"},
        )
        assert child_home_response.status_code == 403

        package_response = client.get(
            f"/api/v2/child-home/{CHILD_ID}/packages/{DEFAULT_PACKAGE_ID}",
            headers={"host": "localhost"},
        )
        assert package_response.status_code == 403

        children_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/children",
            headers={"host": "localhost"},
        )
        assert children_response.status_code == 403

        household_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}",
            headers={"host": "localhost"},
        )
        assert household_response.status_code == 403

        dashboard_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/dashboard",
            headers={"host": "localhost"},
        )
        assert dashboard_response.status_code == 403

        plan_response = client.get(
            f"/api/v2/caregiver/households/{HOUSEHOLD_ID}/plan",
            headers={"host": "localhost"},
        )
        assert plan_response.status_code == 403
    finally:
        HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID] = original_fixture
