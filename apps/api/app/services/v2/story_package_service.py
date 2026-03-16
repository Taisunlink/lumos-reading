from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from app.schemas.v2.story_package import (
    StoryPackageManifestV1,
    StoryPackageMediaV1,
    StoryPackageOverlayV1,
    StoryPackagePageV1,
    StoryPackageSafetyV1,
    StoryPackageTextRunV1,
)
from app.services.v2.fixtures import (
    DEFAULT_STORY_PACKAGE_FIXTURE,
    FIXTURE_TIMESTAMP,
    PACKAGE_FIXTURES,
    StoryPackageFixture,
)


class StoryPackageService(Protocol):
    def get_story_package(self, package_id: UUID) -> StoryPackageManifestV1:
        """Return a single versioned story package."""

    def list_story_packages(self, package_ids: Iterable[UUID]) -> list[StoryPackageManifestV1]:
        """Return story packages in the same order as the provided identifiers."""


def _build_story_package(
    package_id: UUID,
    fixture: StoryPackageFixture,
) -> StoryPackageManifestV1:
    return StoryPackageManifestV1(
        package_id=package_id,
        story_master_id=fixture.story_master_id,
        story_variant_id=fixture.story_variant_id,
        title=fixture.title,
        subtitle=fixture.subtitle,
        language_mode=fixture.language_mode,
        difficulty_level=fixture.difficulty_level,
        age_band=fixture.age_band,
        estimated_duration_sec=fixture.estimated_duration_sec,
        release_channel="pilot",
        cover_image_url=fixture.cover_image_url,
        tags=list(fixture.tags),
        safety=StoryPackageSafetyV1(
            review_status="approved",
            reviewed_at=FIXTURE_TIMESTAMP,
            review_policy_version="2026.03",
        ),
        pages=[
            StoryPackagePageV1(
                page_index=0,
                text_runs=[
                    StoryPackageTextRunV1(
                        text=fixture.text,
                        lang=fixture.language_mode,
                        tts_timing=list(fixture.tts_timing),
                    )
                ],
                media=StoryPackageMediaV1(
                    image_url=fixture.image_url,
                    audio_url=fixture.audio_url,
                ),
                overlays=StoryPackageOverlayV1(
                    vocabulary=list(fixture.vocabulary),
                    caregiver_prompt_ids=list(fixture.caregiver_prompt_ids),
                ),
            )
        ],
    )


class DemoStoryPackageService:
    def get_story_package(self, package_id: UUID) -> StoryPackageManifestV1:
        fixture = PACKAGE_FIXTURES.get(package_id, DEFAULT_STORY_PACKAGE_FIXTURE)
        return _build_story_package(package_id, fixture)

    def list_story_packages(self, package_ids: Iterable[UUID]) -> list[StoryPackageManifestV1]:
        return [self.get_story_package(package_id) for package_id in package_ids]
