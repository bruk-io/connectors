"""Infrastructure client — adapter for external systems."""

import httpx


def get(url: str, headers: dict[str, str] | None = None) -> str:
    """Fetch a URL and return the response text."""
    with httpx.Client() as client:
        response = client.get(url, headers=headers or {})
        response.raise_for_status()
        return response.text
