"""ChefSteps domain operations — pure functions, no I/O."""

import re

_CHEFSTEPS_RECIPE_PATTERN = re.compile(r"^https?://(?:www\.)?chefsteps\.com/activities/([\w-]+)$")

_CHEFSTEPS_API_BASE = "https://www.chefsteps.com/api/v0/activities"


def parse_recipe_url(url: str) -> str:
    """Validate and extract recipe slug from a ChefSteps URL.

    Raise ValueError if the URL is not a valid ChefSteps recipe URL.
    """
    match = _CHEFSTEPS_RECIPE_PATTERN.match(url.strip())
    if not match:
        raise ValueError(
            f"Not a valid ChefSteps recipe URL: {url}\n"
            "Expected format: https://www.chefsteps.com/activities/<slug>"
        )
    return match.group(1)


def recipe_api_url(slug: str) -> str:
    """Build the ChefSteps API URL for a recipe slug."""
    return f"{_CHEFSTEPS_API_BASE}/{slug}"
