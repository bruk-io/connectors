"""LocalStorage Extraction from Browsers

Provide functionality to extract localStorage data from Chromium-based browsers.
This can be used to retrieve authentication tokens, session data, and other
locally stored information from websites.
"""

import contextlib
import json
import logging
import os
import pathlib
import subprocess
import sys
from collections.abc import Callable
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress_stdout() -> Any:
    """Suppress stdout output temporarily."""
    original_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, "w")
        yield
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout


class SupportedBrowser(Enum):
    """Supported browsers."""

    ARC = "arc"
    CHROME = "chrome"
    EDGE = "edge"
    BRAVE = "brave"
    VIVALDI = "vivaldi"
    OPERA = "opera"
    FIREFOX = "firefox"
    SAFARI = "safari"


class LocalStorageExtractor:
    """Extract localStorage data from Chromium-based browsers.

    Read localStorage data directly from browser storage files,
    allowing extraction of authentication tokens, preferences, and other
    data stored by websites.

    Note:
        Only works with Chromium-based browsers (Chrome, Edge, Brave, Arc, etc.).
        Firefox and Safari are not supported. On macOS, Full Disk Access permission
        is required for the terminal or IDE running this code.

    Attributes:
        browser: The browser to extract data from
        browser_path: Path to the browser's localStorage directory
    """

    BROWSER_PATHS = {
        "darwin": {
            SupportedBrowser.ARC: (
                "~/Library/Application Support/Arc/User Data/Default/Local Storage/leveldb"
            ),
            SupportedBrowser.CHROME: (
                "~/Library/Application Support/Google/Chrome/Default/Local Storage/leveldb"
            ),
            SupportedBrowser.EDGE: (
                "~/Library/Application Support/Microsoft Edge/Default/Local Storage/leveldb"
            ),
            SupportedBrowser.BRAVE: (
                "~/Library/Application Support/BraveSoftware/Brave-Browser/"
                "Default/Local Storage/leveldb"
            ),
            SupportedBrowser.VIVALDI: (
                "~/Library/Application Support/Vivaldi/Default/Local Storage/leveldb"
            ),
            SupportedBrowser.OPERA: (
                "~/Library/Application Support/com.operasoftware.Opera/"
                "Default/Local Storage/leveldb"
            ),
        },
        "linux": {
            SupportedBrowser.CHROME: "~/.config/google-chrome/Default/Local Storage/leveldb",
            SupportedBrowser.EDGE: "~/.config/microsoft-edge/Default/Local Storage/leveldb",
            SupportedBrowser.BRAVE: (
                "~/.config/BraveSoftware/Brave-Browser/Default/Local Storage/leveldb"
            ),
            SupportedBrowser.VIVALDI: "~/.config/vivaldi/Default/Local Storage/leveldb",
            SupportedBrowser.OPERA: "~/.config/opera/Default/Local Storage/leveldb",
        },
        "win32": {
            SupportedBrowser.CHROME: (
                r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb"
            ),
            SupportedBrowser.EDGE: (
                r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb"
            ),
            SupportedBrowser.BRAVE: (
                r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"
                r"\Default\Local Storage\leveldb"
            ),
            SupportedBrowser.VIVALDI: (
                r"%LOCALAPPDATA%\Vivaldi\User Data\Default\Local Storage\leveldb"
            ),
            SupportedBrowser.OPERA: (
                r"%APPDATA%\Opera Software\Opera Stable\Default\Local Storage\leveldb"
            ),
        },
    }

    def __init__(self, browser: SupportedBrowser = SupportedBrowser.CHROME):
        """Initialize the LocalStorageExtractor.

        Args:
            browser: The browser to extract localStorage from
        """
        self.browser = browser
        self.browser_path = self._get_browser_path()

    def _get_browser_path(self) -> str:
        """Get the browser's localStorage directory path based on OS."""
        platform = sys.platform

        if platform not in self.BROWSER_PATHS:
            raise ValueError(f"Unsupported platform: {platform}")

        if self.browser not in self.BROWSER_PATHS[platform]:
            raise ValueError(f"Browser {self.browser.value} not supported on {platform}")

        path = self.BROWSER_PATHS[platform][self.browser]

        if platform == "win32":
            path = os.path.expandvars(path)
        return os.path.expanduser(path)

    def _validate_path(self, path: str) -> bool:
        """Validate that a path is safe to access.

        Args:
            path: The path to validate

        Returns:
            True if the path is safe, False otherwise
        """
        try:
            abs_path = os.path.abspath(path)

            home_dir = os.path.expanduser("~")
            valid_prefixes = [home_dir]

            if sys.platform == "win32":
                valid_prefixes.extend(
                    [os.environ.get("LOCALAPPDATA", ""), os.environ.get("APPDATA", "")]
                )

            return any(abs_path.startswith(prefix) for prefix in valid_prefixes if prefix)
        except Exception:
            return False

    def check_access(self) -> bool:
        """Check if we have access to the browser's localStorage directory."""
        try:
            if not self._validate_path(self.browser_path):
                return False

            abs_path = os.path.abspath(self.browser_path)
            if os.path.exists(abs_path):
                os.listdir(abs_path)
                return True
            return False
        except PermissionError, FileNotFoundError:
            return False

    def request_access_permission(self) -> bool:
        """Guide user through permission setup if needed.

        Returns:
            True if access is granted, False otherwise
        """
        if self.check_access():
            return True

        print(f"Full Disk Access required to read {self.browser.value} browser data")

        if sys.platform == "darwin":
            print("\nSteps to grant access:")
            print("1. System Preferences -> Security & Privacy -> Privacy tab")
            print("2. Select 'Full Disk Access' from left sidebar")
            print("3. Click lock icon and enter password")
            print("4. Click '+' and add Terminal (or your Python IDE)")
            print("5. Restart this script")

            subprocess.run(
                [
                    "open",
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles",
                ]
            )

        input("\nPress Enter after granting permission...")

        if self.check_access():
            print("Access granted!")
            return True

        print("Still no access. Please ensure Full Disk Access is enabled.")
        return False

    def extract_all_data(self, domain_filter: str | None = None) -> dict[str, dict[str, Any]]:
        """Extract all localStorage data, optionally filtered by domain.

        Args:
            domain_filter: Optional domain to filter results (e.g., 'github.com')

        Returns:
            Dictionary mapping domains to their localStorage data
        """
        if not self.check_access():
            logger.warning(f"No access to {self.browser.value} localStorage")
            return {}

        try:
            if not self._validate_path(self.browser_path):
                logger.warning(f"Invalid path for {self.browser.value} localStorage")
                return {}

            from ccl_chromium_reader import ccl_chromium_localstorage

            level_db_in_dir = pathlib.Path(self.browser_path)

            if not level_db_in_dir.exists():
                return {}

            results: dict[str, dict[str, Any]] = {}

            with (
                suppress_stdout(),
                ccl_chromium_localstorage.LocalStoreDb(level_db_in_dir) as local_storage,
            ):
                storage_keys = list(local_storage.iter_storage_keys())

                for storage_key in storage_keys:
                    domain = str(storage_key)

                    if domain_filter and domain_filter not in domain:
                        continue

                    domain_data: dict[str, Any] = {}

                    try:
                        for record in local_storage.iter_records_for_storage_key(storage_key):
                            key = str(record.script_key)
                            value: Any = str(record.value)

                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                pass

                            domain_data[key] = value
                    except Exception as e:
                        logger.debug(f"Error reading records for {domain}: {e}")
                        continue

                    if domain_data:
                        results[domain] = domain_data

            return results

        except ImportError:
            logger.error(
                "ccl-chromium-reader not installed. Install with: pip install ccl-chromium-reader"
            )
            return {}
        except Exception as e:
            logger.error(f"Failed to extract localStorage: {e}")
            return {}

    def extract_by_key(self, key_name: str, domain_filter: str | None = None) -> dict[str, Any]:
        """Extract specific localStorage key across all domains.

        Args:
            key_name: The localStorage key to search for
            domain_filter: Optional domain to filter results

        Returns:
            Dictionary mapping domains to the key's value
        """
        all_data = self.extract_all_data(domain_filter)
        results: dict[str, Any] = {}

        for domain, data in all_data.items():
            if key_name in data:
                results[domain] = data[key_name]

        return results

    def extract_for_domain(self, domain: str) -> dict[str, Any]:
        """Extract all localStorage data for a specific domain.

        Args:
            domain: The domain to extract data for (e.g., 'github.com')

        Returns:
            Dictionary of localStorage key-value pairs
        """
        all_data = self.extract_all_data(domain_filter=domain)

        for stored_domain, data in all_data.items():
            if domain in stored_domain:
                return data

        return {}

    def find_authentication_data(
        self, domain_filter: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Search for common authentication-related localStorage keys.

        Look for common patterns in localStorage keys that typically
        contain authentication data like tokens, session IDs, etc.

        Args:
            domain_filter: Optional domain to filter results

        Returns:
            Dictionary mapping domains to their authentication data
        """
        auth_patterns = [
            "token",
            "auth",
            "session",
            "jwt",
            "access_token",
            "refresh_token",
            "api_key",
            "apikey",
            "bearer",
            "credential",
            "user",
            "login",
        ]

        all_data = self.extract_all_data(domain_filter)
        results: dict[str, dict[str, Any]] = {}

        for domain, data in all_data.items():
            auth_data: dict[str, Any] = {}

            for key, value in data.items():
                key_lower = key.lower()
                if any(pattern in key_lower for pattern in auth_patterns):
                    auth_data[key] = value

            if auth_data:
                results[domain] = auth_data

        return results

    def search_values(
        self, search_func: Callable[[str, Any], bool], domain_filter: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Search localStorage using a custom function.

        Args:
            search_func: Function that takes (key, value) and returns True if match
            domain_filter: Optional domain to filter results

        Returns:
            Dictionary mapping domains to matching key-value pairs
        """
        all_data = self.extract_all_data(domain_filter)
        results: dict[str, dict[str, Any]] = {}

        for domain, data in all_data.items():
            matches: dict[str, Any] = {}

            for key, value in data.items():
                if search_func(key, value):
                    matches[key] = value

            if matches:
                results[domain] = matches

        return results
