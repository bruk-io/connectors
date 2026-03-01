"""Unit tests for ChefSteps domain operations."""

import pytest

from connectors.domain.chefsteps.operations import parse_recipe_url, recipe_api_url

# --- parse_recipe_url ---


def test_parse_recipe_url_valid() -> None:
    slug = parse_recipe_url("https://www.chefsteps.com/activities/buttermilk-pancakes")
    assert slug == "buttermilk-pancakes"


def test_parse_recipe_url_without_www() -> None:
    slug = parse_recipe_url("https://chefsteps.com/activities/buttermilk-pancakes")
    assert slug == "buttermilk-pancakes"


def test_parse_recipe_url_http() -> None:
    slug = parse_recipe_url("http://www.chefsteps.com/activities/sous-vide-eggs")
    assert slug == "sous-vide-eggs"


def test_parse_recipe_url_with_trailing_whitespace() -> None:
    slug = parse_recipe_url("  https://www.chefsteps.com/activities/some-recipe  ")
    assert slug == "some-recipe"


def test_parse_recipe_url_invalid_domain() -> None:
    with pytest.raises(ValueError, match="Not a valid ChefSteps recipe URL"):
        parse_recipe_url("https://www.example.com/activities/pancakes")


def test_parse_recipe_url_not_a_url() -> None:
    with pytest.raises(ValueError, match="Not a valid ChefSteps recipe URL"):
        parse_recipe_url("buttermilk pancakes")


def test_parse_recipe_url_missing_slug() -> None:
    with pytest.raises(ValueError, match="Not a valid ChefSteps recipe URL"):
        parse_recipe_url("https://www.chefsteps.com/activities/")


def test_parse_recipe_url_wrong_path() -> None:
    with pytest.raises(ValueError, match="Not a valid ChefSteps recipe URL"):
        parse_recipe_url("https://www.chefsteps.com/recipes/pancakes")


# --- recipe_api_url ---


def test_recipe_api_url() -> None:
    url = recipe_api_url("buttermilk-pancakes")
    assert url == "https://www.chefsteps.com/api/v0/activities/buttermilk-pancakes"


def test_recipe_api_url_different_slug() -> None:
    url = recipe_api_url("sous-vide-eggs")
    assert url == "https://www.chefsteps.com/api/v0/activities/sous-vide-eggs"
