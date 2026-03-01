"""Bon Appetit domain operations — pure functions, no I/O."""

import re

_BON_APPETIT_PATTERN = re.compile(r"^https?://(?:www\.)?bonappetit\.com/recipe/([\w-]+?)(?:\?.*)?$")


def parse_recipe_url(url: str) -> str:
    """Validate and extract recipe slug from a Bon Appetit URL.

    Raise ValueError if the URL is not a valid Bon Appetit recipe URL.
    """
    match = _BON_APPETIT_PATTERN.match(url.strip())
    if not match:
        raise ValueError(
            f"Not a valid Bon Appetit recipe URL: {url}\n"
            "Expected format: https://www.bonappetit.com/recipe/<slug>"
        )
    return match.group(1)
