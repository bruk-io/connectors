"""Google Keep domain operations — pure functions, no I/O."""

import re

_NOTE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")
_KEEP_URL_PATTERN = re.compile(
    r"^https?://keep\.google\.com(?:/#NOTE/|/u/\d+/#NOTE/)([a-zA-Z0-9_-]+)"
)


def parse_note_id(note_id: str) -> str:
    """Validate a Google Keep note ID format.

    Raise ValueError if the ID is not a valid note identifier.
    """
    note_id = note_id.strip()
    if not _NOTE_ID_PATTERN.match(note_id):
        raise ValueError(
            f"Not a valid Google Keep note ID: {note_id}\n"
            "Expected alphanumeric characters, dots, hyphens, or underscores."
        )
    return note_id


def parse_note_url(url: str) -> str:
    """Extract note ID from a Google Keep URL.

    Raise ValueError if the URL is not a valid Google Keep note URL.
    """
    match = _KEEP_URL_PATTERN.match(url.strip())
    if not match:
        raise ValueError(
            f"Not a valid Google Keep note URL: {url}\n"
            "Expected format: https://keep.google.com/#NOTE/<note-id>"
        )
    return match.group(1)
