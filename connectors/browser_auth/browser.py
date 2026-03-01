"""Browser Cookie Extraction

Create HTTP clients using cookies extracted from local browsers.
"""

import logging
from typing import Any

import browser_cookie3
import httpx

from .localstorage import SupportedBrowser

logger = logging.getLogger(__name__)


class BrowserSession:
    """HTTP client that uses cookies from your browser for authentication.

    Create an httpx.Client populated with cookies from your browser,
    allowing authenticated requests to websites where you're already logged in.

    Example:
        ```python
        from connectors.browser_auth import BrowserSession, SupportedBrowser

        session = BrowserSession(
            browser=SupportedBrowser.CHROME,
            domain_filter="github.com"
        )

        response = session.get("https://github.com/notifications")
        print(f"Status: {response.status_code}")
        ```

    Attributes:
        browser: Browser to extract cookies from
        domain_filter: Optional domain to filter cookies (e.g., 'github.com')
        user_agent: Custom user agent string (defaults to Chrome user agent)
        client: The underlying httpx.Client object
    """

    def __init__(
        self,
        browser: SupportedBrowser | str | None = None,
        domain_filter: str | None = None,
        user_agent: str | None = None,
    ):
        """Initialize a BrowserSession.

        Args:
            browser: Browser to extract cookies from (uses all browsers if None)
            domain_filter: Optional domain to filter cookies by (e.g., 'example.com')
            user_agent: Optional custom user agent string
        """
        if browser is None:
            self.browser = "default"
        elif isinstance(browser, str):
            self.browser = browser
        else:
            self.browser = browser.value
        self.domain_filter = domain_filter
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        self.client = self._create_client()

    def _get_cookies(self) -> list[Any]:
        """Extract cookies from the specified browser."""
        if self.browser == "default":
            getter = browser_cookie3.load
        else:
            getter = getattr(browser_cookie3, self.browser, None)
            if getter is None:
                raise ValueError(f"Browser '{self.browser}' is not supported by browser_cookie3")

        try:
            cookies = getter()
            if self.domain_filter:
                filtered_cookies = [c for c in cookies if self.domain_filter in c.domain]
                logger.debug(
                    f"Filtered {len(filtered_cookies)} cookies for domain '{self.domain_filter}'"
                )
                return filtered_cookies
            return list(cookies)
        except Exception as e:
            logger.warning(f"Failed to extract cookies from {self.browser}: {e}")
            return []

    def _create_client(self) -> httpx.Client:
        """Create an httpx Client with browser cookies."""
        jar = httpx.Cookies()

        try:
            cookies = self._get_cookies()
            for c in cookies:
                jar.set(c.name, c.value, domain=c.domain, path=c.path)
            logger.info(f"Loaded {len(cookies)} cookies from {self.browser}")
        except Exception as e:
            logger.error(f"Failed to load cookies from {self.browser}: {e}")

        client = httpx.Client(
            cookies=jar,
            headers={
                "User-Agent": self.user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            follow_redirects=True,
        )

        return client

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a GET request with browser cookies."""
        return self.client.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a POST request with browser cookies."""
        return self.client.post(url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a PUT request with browser cookies."""
        return self.client.put(url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a DELETE request with browser cookies."""
        return self.client.delete(url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a PATCH request with browser cookies."""
        return self.client.patch(url, **kwargs)

    def raw_client(self) -> httpx.Client:
        """Get the underlying httpx.Client object for advanced usage."""
        return self.client

    def get_cookies_dict(self, domain: str | None = None) -> dict[str, str]:
        """Get cookies as a dictionary.

        Args:
            domain: Optional domain to filter cookies by

        Returns:
            Dictionary mapping cookie names to values
        """
        cookies_dict: dict[str, str] = {}
        for cookie in self.client.cookies.jar:
            if domain is None or domain in (cookie.domain or ""):
                cookies_dict[str(cookie.name)] = str(cookie.value)
        return cookies_dict

    def update_headers(self, headers: dict[str, str]) -> None:
        """Update client headers."""
        self.client.headers.update(headers)
