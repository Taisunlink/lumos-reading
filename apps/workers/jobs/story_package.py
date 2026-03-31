from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class StoryPackageArtifactPlan:
    artifact_root_object_key: str
    manifest_object_key: str
    cover_object_key: str | None
    page_media_object_keys: dict[int, dict[str, str]]


def _infer_extension(url: str | None, default_extension: str) -> str:
    if not url:
        return default_extension

    path = urlparse(url).path
    leaf = path.rsplit("/", maxsplit=1)[-1]
    if "." not in leaf:
        return default_extension

    return "." + leaf.rsplit(".", maxsplit=1)[-1]


def build_story_package_artifacts(
    package_payload: Mapping[str, Any],
    build_version: int,
    resolve_public_url: Callable[[str], str],
) -> tuple[dict[str, Any], StoryPackageArtifactPlan]:
    package = deepcopy(dict(package_payload))
    package_id = str(package["package_id"])
    artifact_root_object_key = f"story-packages/runtime/{package_id}/build-{build_version}"
    manifest_object_key = f"{artifact_root_object_key}/manifest.json"

    cover_object_key = None
    if package.get("cover_image_url"):
        cover_extension = _infer_extension(package.get("cover_image_url"), ".png")
        cover_object_key = f"{artifact_root_object_key}/cover{cover_extension}"
        package["cover_image_url"] = resolve_public_url(cover_object_key)

    page_media_object_keys: dict[int, dict[str, str]] = {}
    for page in package.get("pages", []):
        page_index = int(page["page_index"])
        media = dict(page.get("media") or {})
        media_keys: dict[str, str] = {}

        if media.get("image_url"):
            image_extension = _infer_extension(media.get("image_url"), ".png")
            image_object_key = (
                f"{artifact_root_object_key}/pages/{page_index}/image{image_extension}"
            )
            media["image_url"] = resolve_public_url(image_object_key)
            media_keys["image_url"] = image_object_key

        if media.get("audio_url"):
            audio_extension = _infer_extension(media.get("audio_url"), ".mp3")
            audio_object_key = (
                f"{artifact_root_object_key}/pages/{page_index}/audio{audio_extension}"
            )
            media["audio_url"] = resolve_public_url(audio_object_key)
            media_keys["audio_url"] = audio_object_key

        if media:
            page["media"] = media

        page_media_object_keys[page_index] = media_keys

    return package, StoryPackageArtifactPlan(
        artifact_root_object_key=artifact_root_object_key,
        manifest_object_key=manifest_object_key,
        cover_object_key=cover_object_key,
        page_media_object_keys=page_media_object_keys,
    )
