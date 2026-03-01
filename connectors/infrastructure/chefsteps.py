"""ChefSteps API client — authenticated requests using browser credentials."""

import logging
from typing import Any

from connectors.browser_auth import BrowserSession, LocalStorageExtractor

logger = logging.getLogger(__name__)

_AUTH0_CLIENT_ID = "F5RLvKcdyEmOG7AliHFTTwnxNkikR03C"


def _extract_auth0_token() -> str | None:
    """Extract Auth0 bearer token from browser localStorage."""
    try:
        extractor = LocalStorageExtractor()
        data = extractor.extract_all_data(domain_filter="chefsteps.com")
    except Exception as e:
        logger.debug(f"Failed to read localStorage: {e}")
        return None

    for _domain, entries in data.items():
        for key, value in entries.items():
            if "auth0spajs" not in key.lower():
                continue
            if not isinstance(value, dict):
                continue
            body: dict[str, Any] = value.get("body", {})
            token = body.get("access_token")
            if isinstance(token, str) and token:
                return token
    return None


def fetch_recipe(api_url: str) -> str:
    """Fetch a ChefSteps recipe as JSON using browser credentials.

    Use browser cookies and Auth0 bearer token extracted from localStorage.
    """
    session = BrowserSession(domain_filter="chefsteps.com")
    session.update_headers({"Accept": "application/json, text/plain, */*"})

    token = _extract_auth0_token()
    if token:
        session.update_headers({"Authorization": f"Bearer {token}"})
    else:
        logger.warning(
            "Could not extract Auth0 token from browser localStorage. "
            "Request may fail if cookies alone are insufficient."
        )

    response = session.get(api_url)
    response.raise_for_status()
    return response.text
