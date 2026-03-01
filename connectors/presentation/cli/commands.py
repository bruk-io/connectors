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


@cli.group("bon-appetit")
def bon_appetit() -> None:
    """Bon Appetit recipe commands."""
    pass


@bon_appetit.command("get-recipe")
@click.argument("urls", nargs=-1, required=True)
def get_recipe_bon_appetit(urls: tuple[str, ...]) -> None:
    """Fetch raw HTML from Bon Appetit recipe pages.

    Pass one or more Bon Appetit recipe URLs, e.g.:
    https://www.bonappetit.com/recipe/green-chile-puttanesca-pork-chops
    """
    from connectors.domain.bon_appetit import parse_recipe_url
    from connectors.infrastructure.browser import fetch_authenticated

    for url in urls:
        parse_recipe_url(url)

    for url in urls:
        click.echo(fetch_authenticated(url, domain="bonappetit.com"))


@cli.group("google-keep")
def google_keep() -> None:
    """Google Keep note commands."""
    pass


@google_keep.command("list-notes")
def list_notes() -> None:
    """List all Google Keep notes."""
    from connectors.infrastructure.google_keep import list_notes as _list_notes

    click.echo(_list_notes())


@google_keep.command("get-note")
@click.argument("note_id")
def get_note(note_id: str) -> None:
    """Fetch a single Google Keep note by ID."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import get_note as _get_note

    validated_id = parse_note_id(note_id)
    click.echo(_get_note(validated_id))


@google_keep.command("create-note")
@click.option("--title", required=True, help="Note title.")
@click.option("--content", required=True, help="Note text content.")
def create_note(title: str, content: str) -> None:
    """Create a new Google Keep note."""
    from connectors.infrastructure.google_keep import create_note as _create_note

    click.echo(_create_note(title, content))


@google_keep.command("create-list")
@click.option("--title", required=True, help="List title.")
@click.argument("items", nargs=-1, required=True)
def create_list(title: str, items: tuple[str, ...]) -> None:
    """Create a new Google Keep checklist.

    Pass list items as arguments, e.g.:
    connectors google-keep create-list --title "Groceries" "Milk" "Eggs" "Bread"
    """
    from connectors.infrastructure.google_keep import create_list as _create_list

    click.echo(_create_list(title, list(items)))


@google_keep.command("check-item")
@click.argument("note_id")
@click.argument("item_text")
def check_item(note_id: str, item_text: str) -> None:
    """Check a list item by its text."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import check_item as _check_item

    validated_id = parse_note_id(note_id)
    click.echo(_check_item(validated_id, item_text, checked=True))


@google_keep.command("uncheck-item")
@click.argument("note_id")
@click.argument("item_text")
def uncheck_item(note_id: str, item_text: str) -> None:
    """Uncheck a list item by its text."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import check_item as _check_item

    validated_id = parse_note_id(note_id)
    click.echo(_check_item(validated_id, item_text, checked=False))


@google_keep.command("delete-note")
@click.argument("note_id")
def delete_note(note_id: str) -> None:
    """Delete a Google Keep note by ID."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import delete_note as _delete_note

    validated_id = parse_note_id(note_id)
    click.echo(_delete_note(validated_id))


@google_keep.command("pin-note")
@click.argument("note_id")
def pin_note(note_id: str) -> None:
    """Pin a Google Keep note."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import pin_note as _pin_note

    validated_id = parse_note_id(note_id)
    click.echo(_pin_note(validated_id, pinned=True))


@google_keep.command("unpin-note")
@click.argument("note_id")
def unpin_note(note_id: str) -> None:
    """Unpin a Google Keep note."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import pin_note as _pin_note

    validated_id = parse_note_id(note_id)
    click.echo(_pin_note(validated_id, pinned=False))


@google_keep.command("download-attachment")
@click.argument("note_id")
@click.argument("attachment_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path.")
def download_attachment(note_id: str, attachment_id: str, output: str | None) -> None:
    """Download an attachment from a Google Keep note."""
    from connectors.domain.google_keep import parse_note_id
    from connectors.infrastructure.google_keep import (
        download_attachment as _download_attachment,
    )

    validated_note_id = parse_note_id(note_id)
    data = _download_attachment(validated_note_id, attachment_id)
    if output:
        with open(output, "wb") as f:
            f.write(data)
        click.echo(f"Saved to {output}")
    else:
        click.get_binary_stream("stdout").write(data)
