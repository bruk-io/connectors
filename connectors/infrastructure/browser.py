"""Browser-authenticated HTTP fetching."""

from connectors.browser_auth import BrowserSession


def fetch_authenticated(url: str, domain: str) -> str:
    """Fetch a URL using browser cookies for authentication.

    Create a BrowserSession filtered to the given domain and return
    the response text.
    """
    session = BrowserSession(domain_filter=domain)
    response = session.get(url)
    response.raise_for_status()
    return response.text
