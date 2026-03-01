"""Unit tests for Serious Eats domain operations."""

import pytest

from connectors.domain.serious_eats.operations import parse_recipe_url

# --- parse_recipe_url ---


def test_parse_recipe_url_valid() -> None:
    slug = parse_recipe_url("https://www.seriouseats.com/air-fryer-halloumi-bites-recipe-11914176")
    assert slug == "air-fryer-halloumi-bites-recipe-11914176"


def test_parse_recipe_url_without_www() -> None:
    slug = parse_recipe_url("https://seriouseats.com/best-new-york-cheesecake-recipe")
    assert slug == "best-new-york-cheesecake-recipe"


def test_parse_recipe_url_http() -> None:
    slug = parse_recipe_url("http://www.seriouseats.com/sous-vide-steak-guide")
    assert slug == "sous-vide-steak-guide"


def test_parse_recipe_url_with_trailing_whitespace() -> None:
    slug = parse_recipe_url("  https://www.seriouseats.com/some-recipe  ")
    assert slug == "some-recipe"


def test_parse_recipe_url_strips_query_params() -> None:
    slug = parse_recipe_url("https://www.seriouseats.com/some-recipe?print")
    assert slug == "some-recipe"


def test_parse_recipe_url_invalid_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid Serious Eats recipe URL"):
        parse_recipe_url("https://www.example.com/some-recipe")


def test_parse_recipe_url_not_a_url() -> None:
    with pytest.raises(ValueError, match="Not a valid Serious Eats recipe URL"):
        parse_recipe_url("halloumi bites")


def test_parse_recipe_url_bare_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid Serious Eats recipe URL"):
        parse_recipe_url("https://www.seriouseats.com/")
