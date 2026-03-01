"""NYT Cooking domain operations — pure functions, no I/O."""

import re

_NYT_COOKING_PATTERN = re.compile(r"^https?://cooking\.nytimes\.com/recipes/(\d+[\w-]*)$")


def parse_recipe_url(url: str) -> str:
    """Validate and extract recipe slug from a NYT Cooking URL.

    Raise ValueError if the URL is not a valid NYT Cooking recipe URL.
    """
    match = _NYT_COOKING_PATTERN.match(url.strip())
    if not match:
        raise ValueError(
            f"Not a valid NYT Cooking recipe URL: {url}\n"
            "Expected format: https://cooking.nytimes.com/recipes/<id>-<slug>"
        )
    return match.group(1)
