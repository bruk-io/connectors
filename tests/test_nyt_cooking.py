"""Unit tests for NYT Cooking domain operations."""

import pytest

from connectors.domain.nyt_cooking.operations import parse_recipe_url

# --- parse_recipe_url ---


def test_parse_recipe_url_valid() -> None:
    slug = parse_recipe_url("https://cooking.nytimes.com/recipes/1015416-chicken-cacciatore")
    assert slug == "1015416-chicken-cacciatore"


def test_parse_recipe_url_numeric_only() -> None:
    slug = parse_recipe_url("https://cooking.nytimes.com/recipes/1015416")
    assert slug == "1015416"


def test_parse_recipe_url_with_trailing_whitespace() -> None:
    slug = parse_recipe_url("  https://cooking.nytimes.com/recipes/1015416-chicken  ")
    assert slug == "1015416-chicken"


def test_parse_recipe_url_invalid_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid NYT Cooking recipe URL"):
        parse_recipe_url("https://www.nytimes.com/recipes/123")


def test_parse_recipe_url_not_a_url() -> None:
    with pytest.raises(ValueError, match="Not a valid NYT Cooking recipe URL"):
        parse_recipe_url("chicken cacciatore")


def test_parse_recipe_url_missing_id() -> None:
    with pytest.raises(ValueError, match="Not a valid NYT Cooking recipe URL"):
        parse_recipe_url("https://cooking.nytimes.com/recipes/")
