"""Browser Authentication Library

Extract cookies and localStorage data from browsers to enable authenticated HTTP sessions.
"""

from .browser import BrowserSession
from .localstorage import LocalStorageExtractor, SupportedBrowser

__all__ = [
    "BrowserSession",
    "LocalStorageExtractor",
    "SupportedBrowser",
]
