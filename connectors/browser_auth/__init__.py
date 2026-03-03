"""Browser Authentication Library

Extract cookies and localStorage data from browsers to enable authenticated HTTP sessions.
"""

from .browser import BrowserSession, SessionExpiredError
from .localstorage import LocalStorageExtractor, SupportedBrowser

__all__ = [
    "BrowserSession",
    "LocalStorageExtractor",
    "SessionExpiredError",
    "SupportedBrowser",
]
