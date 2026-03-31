from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PackageAccessEvent:
    household_id: UUID
    child_id: UUID | None
    package_id: UUID
    surface: str
    outcome: str
    reason: str
    occurred_at: datetime


PACKAGE_ACCESS_EVENTS: list[PackageAccessEvent] = []


def record_entitled_package_delivery(
    household_id: UUID,
    child_id: UUID,
    package_id: UUID,
    surface: str,
    reason: str,
    occurred_at: datetime,
) -> None:
    PACKAGE_ACCESS_EVENTS.append(
        PackageAccessEvent(
            household_id=household_id,
            child_id=child_id,
            package_id=package_id,
            surface=surface,
            outcome="entitled_delivery",
            reason=reason,
            occurred_at=occurred_at,
        )
    )


def record_blocked_package_request(
    household_id: UUID,
    child_id: UUID | None,
    package_id: UUID,
    surface: str,
    reason: str,
    occurred_at: datetime,
) -> None:
    PACKAGE_ACCESS_EVENTS.append(
        PackageAccessEvent(
            household_id=household_id,
            child_id=child_id,
            package_id=package_id,
            surface=surface,
            outcome="blocked_request",
            reason=reason,
            occurred_at=occurred_at,
        )
    )


def list_package_access_events() -> list[PackageAccessEvent]:
    return list(PACKAGE_ACCESS_EVENTS)


def reset_package_access_events() -> None:
    PACKAGE_ACCESS_EVENTS.clear()
