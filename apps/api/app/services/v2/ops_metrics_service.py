from collections.abc import Callable
from datetime import datetime

from app.schemas.v2.monetization import OpsMetricsSnapshotV1
from app.services.v2.entitlement_service import EntitlementService
from app.services.v2.package_access_store import list_package_access_events
from app.services.v2.progress_service import ProgressService
from app.services.v2.weekly_value_service import WeeklyValueService


class OpsMetricsService:
    def __init__(
        self,
        entitlement_service: EntitlementService,
        progress_service: ProgressService,
        weekly_value_service: WeeklyValueService,
        clock: Callable[[], datetime],
    ):
        self.entitlement_service = entitlement_service
        self.progress_service = progress_service
        self.weekly_value_service = weekly_value_service
        self.clock = clock

    def get_snapshot(self) -> OpsMetricsSnapshotV1:
        household_ids = self.entitlement_service.list_household_ids()
        entitlements = [
            self.entitlement_service.get_household_entitlement(household_id)
            for household_id in household_ids
        ]
        weekly_reports = [
            self.weekly_value_service.get_weekly_value_report(household_id)
            for household_id in household_ids
        ]
        access_events = list_package_access_events()
        completed_sessions = 0
        reuse_signals = 0

        for household_id in household_ids:
            progress = self.progress_service.get_household_progress(household_id)
            completed_sessions += progress.progress_metrics.completed_sessions
            reread_signals = next(
                (
                    report.reread_sessions
                    for report in weekly_reports
                    if report.household_id == household_id
                ),
                0,
            )
            reuse_signals += progress.progress_metrics.audio_replays + reread_signals

        average_value_score = (
            round(
                sum(report.value_score for report in weekly_reports) / len(weekly_reports),
                1,
            )
            if weekly_reports
            else 0.0
        )

        return OpsMetricsSnapshotV1(
            generated_at=self.clock(),
            households_in_scope=len(household_ids),
            households_in_trial=sum(
                1 for item in entitlements if item.subscription_status == "trial_active"
            ),
            households_with_paid_access=sum(
                1 for item in entitlements if item.access_state in {"paid", "grace"}
            ),
            entitled_package_deliveries=sum(
                1 for item in access_events if item.outcome == "entitled_delivery"
            ),
            blocked_package_requests=sum(
                1 for item in access_events if item.outcome == "blocked_request"
            ),
            completed_sessions=completed_sessions,
            reuse_signals=reuse_signals,
            average_weekly_value_score=average_value_score,
        )
