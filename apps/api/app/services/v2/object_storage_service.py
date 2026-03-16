from typing import Protocol
from urllib.parse import quote

from app.core.config import settings


class ObjectStorageService(Protocol):
    def get_public_url(self, object_key: str) -> str:
        """Resolve an object key to a public URL."""

    def get_signed_url(self, object_key: str, expires_in_seconds: int) -> str:
        """Resolve an object key to a signed URL."""


class PlaceholderOssStorageService:
    """Placeholder OSS adapter until real bucket integration is wired in."""

    def __init__(self, public_base_url: str | None = None):
        self.public_base_url = self._resolve_public_base_url(public_base_url)

    def get_public_url(self, object_key: str) -> str:
        normalized_key = self._normalize_object_key(object_key)
        if not normalized_key:
            return self.public_base_url
        return f"{self.public_base_url}/{normalized_key}"

    def get_signed_url(self, object_key: str, expires_in_seconds: int) -> str:
        del expires_in_seconds
        return self.get_public_url(object_key)

    @staticmethod
    def _normalize_object_key(object_key: str) -> str:
        return "/".join(
            quote(segment)
            for segment in object_key.lstrip("/").split("/")
            if segment
        )

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        return base_url.rstrip("/")

    @classmethod
    def _resolve_public_base_url(cls, public_base_url: str | None) -> str:
        if public_base_url:
            return cls._normalize_base_url(public_base_url)

        if settings.oss_public_base_url:
            return cls._normalize_base_url(settings.oss_public_base_url)

        if settings.oss_bucket_name and settings.oss_endpoint:
            endpoint = settings.oss_endpoint.removeprefix("https://").removeprefix("http://").rstrip("/")
            return f"https://{settings.oss_bucket_name}.{endpoint}"

        return "https://oss-placeholder.lumosreading.local"
