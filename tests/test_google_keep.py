"""Unit tests for Google Keep domain operations."""

import pytest

from connectors.domain.google_keep.operations import parse_note_id, parse_note_url

# --- parse_note_id ---


def test_parse_note_id_valid_alphanumeric() -> None:
    assert parse_note_id("abc123") == "abc123"


def test_parse_note_id_valid_with_hyphens() -> None:
    assert parse_note_id("note-id-123") == "note-id-123"


def test_parse_note_id_valid_with_underscores() -> None:
    assert parse_note_id("note_id_123") == "note_id_123"


def test_parse_note_id_valid_client_id_format() -> None:
    assert parse_note_id("1772387787263.2005457316") == "1772387787263.2005457316"


def test_parse_note_id_valid_server_id_format() -> None:
    sid = "1890nwYI5TbB_lhH1A-AArlB6feZkQYhf6Hw2cM_w61kB46xfCa-k5KvvtiSzDRex"
    assert parse_note_id(sid) == sid


def test_parse_note_id_strips_whitespace() -> None:
    assert parse_note_id("  abc123  ") == "abc123"


def test_parse_note_id_empty_string() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note ID"):
        parse_note_id("")


def test_parse_note_id_whitespace_only() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note ID"):
        parse_note_id("   ")


def test_parse_note_id_invalid_characters() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note ID"):
        parse_note_id("note id with spaces")


def test_parse_note_id_special_characters() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note ID"):
        parse_note_id("note/id")


# --- parse_note_url ---


def test_parse_note_url_valid_hash_format() -> None:
    note_id = parse_note_url("https://keep.google.com/#NOTE/abc123")
    assert note_id == "abc123"


def test_parse_note_url_valid_user_format() -> None:
    note_id = parse_note_url("https://keep.google.com/u/0/#NOTE/abc123")
    assert note_id == "abc123"


def test_parse_note_url_valid_user_1() -> None:
    note_id = parse_note_url("https://keep.google.com/u/1/#NOTE/note-id-456")
    assert note_id == "note-id-456"


def test_parse_note_url_strips_whitespace() -> None:
    note_id = parse_note_url("  https://keep.google.com/#NOTE/abc123  ")
    assert note_id == "abc123"


def test_parse_note_url_invalid_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note URL"):
        parse_note_url("https://notes.google.com/#NOTE/abc123")


def test_parse_note_url_missing_note_fragment() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note URL"):
        parse_note_url("https://keep.google.com/")


def test_parse_note_url_not_a_url() -> None:
    with pytest.raises(ValueError, match="Not a valid Google Keep note URL"):
        parse_note_url("google keep note")


def test_parse_note_url_http_also_accepted() -> None:
    note_id = parse_note_url("http://keep.google.com/#NOTE/abc123")
    assert note_id == "abc123"
