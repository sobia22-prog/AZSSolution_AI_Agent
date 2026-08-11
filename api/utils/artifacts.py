"""Helpers for workflow run artifact access."""

from api.constants import BACKEND_API_ENDPOINT


def artifact_url(
    token: str | None, artifact: str, fallback: str | None = None
) -> str | None:
    if not token:
        return fallback
    base_endpoint = BACKEND_API_ENDPOINT.rstrip("/") if BACKEND_API_ENDPOINT else ""
    return f"{base_endpoint}/api/v1/public/download/workflow/{token}/{artifact}"
