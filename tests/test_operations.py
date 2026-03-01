"""Tests for domain operations."""

from connectors.domain.operations import get_status, greet


def test_greet() -> None:
    assert greet("world") == "Hello, world!"


def test_greet_name() -> None:
    assert greet("Bruk") == "Hello, Bruk!"


def test_get_status() -> None:
    status = get_status()
    assert status["name"] == "connectors"
    assert status["version"] == "0.1.0"
    assert status["status"] == "running"
