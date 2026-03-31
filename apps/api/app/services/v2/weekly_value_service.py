from collections import Counter
from collections.abc import Callable
from datetime import datetime, timedelta
from uuid import UUID

from app.schemas.v2.monetization import WeeklyValueHighlightV1, WeeklyValueReportV1
from app.schemas.v2.reading import ReadingEventV1
from app.services.v2.progress_service import ProgressService


def _payload_number(event: ReadingEventV1, key: str) -> int:
    value = event.payload.get(key)
    return int(value) if isinstance(value, (int, float)) else 0


class WeeklyValueService:
    def __init__(
        self,
        progress_service: ProgressService,
        clock: Callable[[], datetime],
    ):
        self.progress_service = progress_service
        self.clock = clock

    def get_weekly_value_report(self, household_id: UUID) -> WeeklyValueReportV1:
        generated_at = self.clock()
        progress = self.progress_service.get_household_progress(household_id)
        period_end = max(
            [generated_at, *[event.occurred_at for event in progress.recent_events]],
            default=generated_at,
        )
        period_start = period_end - timedelta(days=7)
        window_events = [
            event
            for event in progress.recent_events
            if period_start <= event.occurred_at <= period_end
        ]
        completed_sessions = [
            event for event in window_events if event.event_type == "session_completed"
        ]
        completed_packages = Counter(str(event.package_id) for event in completed_sessions)
        total_dwell_ms = sum(_payload_number(event, "dwell_ms") for event in completed_sessions)
        total_reading_minutes = round(total_dwell_ms / 60000)
        reread_sessions = sum(
            count - 1 for count in completed_packages.values() if count > 1
        )
        caregiver_prompt_completions = sum(
            1 for event in window_events if event.event_type == "caregiver_prompt_completed"
        )
        value_score = min(
            100,
            len(completed_sessions) * 25
            + len(completed_packages) * 15
            + min(total_reading_minutes, 20)
            + reread_sessions * 10
            + caregiver_prompt_completions * 10,
        )

        highlights = [
            WeeklyValueHighlightV1(
                code="completed_sessions",
                title="Completed reading loop",
                detail=(
                    f"{len(completed_sessions)} completed session(s) and "
                    f"{total_reading_minutes} minute(s) of finished reading this week."
                ),
            )
        ]

        if reread_sessions > 0:
            highlights.append(
                WeeklyValueHighlightV1(
                    code="reread",
                    title="Rereading signal",
                    detail=f"{reread_sessions} reread session(s) suggest voluntary reuse.",
                )
            )
        elif progress.progress_metrics.audio_replays > 0:
            highlights.append(
                WeeklyValueHighlightV1(
                    code="replay_signal",
                    title="Replay signal",
                    detail=(
                        f"{progress.progress_metrics.audio_replays} audio replay event(s) show "
                        "the child is revisiting familiar moments."
                    ),
                )
            )

        if caregiver_prompt_completions > 0:
            highlights.append(
                WeeklyValueHighlightV1(
                    code="caregiver_prompt",
                    title="Caregiver participation",
                    detail=(
                        f"{caregiver_prompt_completions} caregiver prompt completion(s) were "
                        "captured in the same weekly loop."
                    ),
                )
            )

        return WeeklyValueReportV1(
            household_id=household_id,
            period_start=period_start,
            period_end=period_end,
            completed_sessions=len(completed_sessions),
            total_reading_minutes=max(0, total_reading_minutes),
            distinct_packages_completed=len(completed_packages),
            reread_sessions=reread_sessions,
            caregiver_prompt_completions=caregiver_prompt_completions,
            value_score=value_score,
            highlights=highlights,
            generated_at=generated_at,
        )
