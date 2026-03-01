"""Click CLI commands."""

import json

import click

from connectors.domain import operations


@click.group()
def cli() -> None:
    """Unofficial API connectors SDK and CLI"""
    pass


@cli.command()
@click.argument("name", default="world")
def greet(name: str) -> None:
    """Greet someone."""
    click.echo(operations.greet(name))


@cli.command()
def status() -> None:
    """Show application status."""
    result = operations.get_status()
    click.echo(json.dumps(result, indent=2))


@cli.group("nyt-cooking")
def nyt_cooking() -> None:
    """NYT Cooking recipe commands."""
    pass


@nyt_cooking.command("get-recipe")
@click.argument("urls", nargs=-1, required=True)
def get_recipe(urls: tuple[str, ...]) -> None:
    """Fetch raw HTML from NYT Cooking recipe pages.

    Pass one or more NYT Cooking recipe URLs, e.g.:
    https://cooking.nytimes.com/recipes/1015416-chicken-cacciatore
    """
    from connectors.domain.nyt_cooking import parse_recipe_url
    from connectors.infrastructure.browser import fetch_authenticated

    for url in urls:
        parse_recipe_url(url)

    for url in urls:
        click.echo(fetch_authenticated(url, domain="nytimes.com"))


@cli.group("chefsteps")
def chefsteps() -> None:
    """ChefSteps recipe commands."""
    pass


@chefsteps.command("get-recipe")
@click.argument("urls", nargs=-1, required=True)
def get_recipe_chefsteps(urls: tuple[str, ...]) -> None:
    """Fetch raw JSON from ChefSteps recipe API.

    Pass one or more ChefSteps recipe URLs, e.g.:
    https://www.chefsteps.com/activities/buttermilk-pancakes
    """
    from connectors.domain.chefsteps import parse_recipe_url, recipe_api_url
    from connectors.infrastructure.chefsteps import fetch_recipe

    slugs = [parse_recipe_url(url) for url in urls]

    for slug in slugs:
        api_url = recipe_api_url(slug)
        click.echo(fetch_recipe(api_url))


@cli.group("serious-eats")
def serious_eats() -> None:
    """Serious Eats recipe commands."""
    pass


@serious_eats.command("get-recipe")
@click.argument("urls", nargs=-1, required=True)
def get_recipe_serious_eats(urls: tuple[str, ...]) -> None:
    """Fetch raw HTML from Serious Eats print recipe pages.

    Pass one or more Serious Eats recipe URLs, e.g.:
    https://www.seriouseats.com/air-fryer-halloumi-bites-recipe-11914176
    """
    from connectors.domain.serious_eats import parse_recipe_url
    from connectors.infrastructure.browser import fetch_authenticated

    for url in urls:
        parse_recipe_url(url)

    for url in urls:
        click.echo(fetch_authenticated(url, domain="seriouseats.com"))
