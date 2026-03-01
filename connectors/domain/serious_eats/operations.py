"""Serious Eats domain operations — pure functions, no I/O."""

import re

_SERIOUS_EATS_PATTERN = re.compile(r"^https?://(?:www\.)?seriouseats\.com/([\w-]+?)(?:\?.*)?$")


def parse_recipe_url(url: str) -> str:
    """Validate and extract recipe slug from a Serious Eats URL.

    Raise ValueError if the URL is not a valid Serious Eats recipe URL.
    """
    match = _SERIOUS_EATS_PATTERN.match(url.strip())
    if not match:
        raise ValueError(
            f"Not a valid Serious Eats recipe URL: {url}\n"
            "Expected format: https://www.seriouseats.com/<slug>"
        )
    return match.group(1)
