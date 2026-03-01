"""NYT Cooking domain — URL validation and raw HTML fetching."""

from connectors.domain.nyt_cooking.operations import parse_recipe_url

__all__ = [
    "parse_recipe_url",
]
