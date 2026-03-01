"""Unit tests for Bon Appetit domain operations."""

import pytest

from connectors.domain.bon_appetit.operations import parse_recipe_url

# --- parse_recipe_url ---


def test_parse_recipe_url_valid() -> None:
    slug = parse_recipe_url("https://www.bonappetit.com/recipe/green-chile-puttanesca-pork-chops")
    assert slug == "green-chile-puttanesca-pork-chops"


def test_parse_recipe_url_without_www() -> None:
    slug = parse_recipe_url("https://bonappetit.com/recipe/bas-best-bolognese")
    assert slug == "bas-best-bolognese"


def test_parse_recipe_url_http() -> None:
    slug = parse_recipe_url("http://www.bonappetit.com/recipe/simple-roast-chicken")
    assert slug == "simple-roast-chicken"


def test_parse_recipe_url_with_trailing_whitespace() -> None:
    slug = parse_recipe_url("  https://www.bonappetit.com/recipe/some-recipe  ")
    assert slug == "some-recipe"


def test_parse_recipe_url_strips_query_params() -> None:
    slug = parse_recipe_url("https://www.bonappetit.com/recipe/some-recipe?print")
    assert slug == "some-recipe"


def test_parse_recipe_url_invalid_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid Bon Appetit recipe URL"):
        parse_recipe_url("https://www.example.com/recipe/some-recipe")


def test_parse_recipe_url_not_a_url() -> None:
    with pytest.raises(ValueError, match="Not a valid Bon Appetit recipe URL"):
        parse_recipe_url("pork chops recipe")


def test_parse_recipe_url_bare_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid Bon Appetit recipe URL"):
        parse_recipe_url("https://www.bonappetit.com/")


def test_parse_recipe_url_missing_slug() -> None:
    with pytest.raises(ValueError, match="Not a valid Bon Appetit recipe URL"):
        parse_recipe_url("https://www.bonappetit.com/recipe/")


def test_parse_recipe_url_wrong_path() -> None:
    with pytest.raises(ValueError, match="Not a valid Bon Appetit recipe URL"):
        parse_recipe_url("https://www.bonappetit.com/story/best-cookbooks-2024")
