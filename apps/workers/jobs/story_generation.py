from dataclasses import dataclass
import os
from typing import Any
from uuid import uuid4


PROVIDER_ENV_VARS = {
    "qwen": "QWEN_API_KEY",
    "vertex": "GOOGLE_APPLICATION_CREDENTIALS",
    "openai": "OPENAI_API_KEY",
}


@dataclass
class DraftGenerationResult:
    package_preview: dict[str, Any]
    operator_notes: list[str]


@dataclass
class MediaGenerationResult:
    package_preview: dict[str, Any]
    attempts: list[dict[str, Any]]
    selected_provider: str
    generated_asset_keys: list[str]


def build_story_package_draft_from_brief(
    brief: dict[str, Any],
    package_id: str,
) -> DraftGenerationResult:
    language_mode = brief["language_mode"]
    page_count = brief["desired_page_count"]
    title = brief["title"]
    theme = brief["theme"]
    premise = brief["premise"]

    pages = [
        {
            "page_index": index,
            "text_runs": [
                {
                    "text": _build_page_text(
                        language_mode=language_mode,
                        title=title,
                        theme=theme,
                        premise=premise,
                        page_index=index,
                        page_count=page_count,
                    ),
                    "lang": language_mode,
                    "tts_timing": [0, 320, 760, 1180],
                }
            ],
            "overlays": {
                "vocabulary": [theme, "review", "draft"],
                "caregiver_prompt_ids": [f"ai-draft-prompt-{index + 1}"],
            },
        }
        for index in range(page_count)
    ]

    package_preview = {
        "schema_version": "story-package.v1",
        "package_id": package_id,
        "story_master_id": str(uuid4()),
        "story_variant_id": str(uuid4()),
        "title": title,
        "subtitle": _build_subtitle(language_mode, theme, premise),
        "language_mode": language_mode,
        "difficulty_level": "L2",
        "age_band": brief["age_band"],
        "estimated_duration_sec": page_count * 150,
        "release_channel": "internal",
        "cover_image_url": None,
        "tags": [theme, "ai-generated", "review-required"],
        "safety": {
            "review_status": "limited_release",
            "reviewed_at": None,
            "review_policy_version": "2026.04-ai-draft",
        },
        "pages": pages,
    }

    return DraftGenerationResult(
        package_preview=package_preview,
        operator_notes=[
            f"AI draft assembled from brief '{title}' with {page_count} generated pages.",
            f"Premise: {premise}",
        ],
    )


def generate_story_package_media(
    package_preview: dict[str, Any],
    provider_preference: str | None,
    resolve_public_url,
) -> MediaGenerationResult:
    package_id = package_preview["package_id"]
    provider_order = _build_provider_order(provider_preference)
    attempts: list[dict[str, Any]] = []
    selected_provider = "placeholder"

    for provider in provider_order:
        if provider == "placeholder":
            attempts.append(
                {
                    "provider": provider,
                    "status": "succeeded",
                    "reason": "placeholder_generation",
                }
            )
            selected_provider = provider
            break

        env_var = PROVIDER_ENV_VARS.get(provider)
        if env_var and os.environ.get(env_var):
            attempts.append(
                {
                    "provider": provider,
                    "status": "succeeded",
                    "reason": "credentials_present",
                }
            )
            selected_provider = provider
            break

        attempts.append(
            {
                "provider": provider,
                "status": "failed",
                "reason": "credentials_unavailable",
            }
        )

    asset_root = f"story-packages/generated/{package_id}/{selected_provider}"
    generated_asset_keys = [f"{asset_root}/cover.png"]

    updated_preview = {
        **package_preview,
        "cover_image_url": resolve_public_url(f"{asset_root}/cover.png"),
        "pages": [],
    }

    for page in package_preview["pages"]:
        page_asset_root = f"{asset_root}/pages/{page['page_index']}"
        generated_asset_keys.extend(
            [
                f"{page_asset_root}/image.png",
                f"{page_asset_root}/audio.mp3",
            ]
        )
        updated_preview["pages"].append(
            {
                **page,
                "media": {
                    "image_url": resolve_public_url(f"{page_asset_root}/image.png"),
                    "audio_url": resolve_public_url(f"{page_asset_root}/audio.mp3"),
                },
            }
        )

    return MediaGenerationResult(
        package_preview=updated_preview,
        attempts=attempts,
        selected_provider=selected_provider,
        generated_asset_keys=generated_asset_keys,
    )


def _build_provider_order(provider_preference: str | None) -> list[str]:
    candidates = [provider_preference, "qwen", "vertex", "openai", "placeholder"]
    ordered: list[str] = []

    for candidate in candidates:
        if candidate and candidate not in ordered:
            ordered.append(candidate)

    return ordered


def _build_subtitle(language_mode: str, theme: str, premise: str) -> str:
    if language_mode.startswith("zh"):
        return f"围绕{theme}的可审稿 AI 草稿。{premise}"

    return f"Reviewable AI draft about {theme}. {premise}"


def _build_page_text(
    language_mode: str,
    title: str,
    theme: str,
    premise: str,
    page_index: int,
    page_count: int,
) -> str:
    if language_mode.startswith("zh"):
        opening = f"{title}从一个关于{theme}的小问题开始。"
        middle = f"第{page_index + 1}页继续展开：{premise}"
        ending = f"到最后一页，孩子会看到{theme}如何落回日常选择。"
    else:
        opening = f"{title} opens with a small question about {theme}."
        middle = f"Page {page_index + 1} continues the premise: {premise}"
        ending = f"By the last page, {theme} returns as a calm everyday choice."

    if page_index == 0:
        return opening

    if page_index == page_count - 1:
        return ending

    return middle
