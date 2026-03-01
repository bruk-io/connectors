"""Google Keep command protocol — parse snapshots and build mutation commands.

Google Keep's internal API uses a serialized command protocol for list mutations.
Commands are JSON arrays sent via the sync endpoint's
``clientChanges.commandBundles[].serializedCommands`` field.

All functions here are pure — no I/O, no side effects.
"""

import json
from typing import Any

from connectors.domain.google_keep.types import CheckboxItem, ListSnapshot

# ---------------------------------------------------------------------------
# Parsing: snapshot command stream → structured data
# ---------------------------------------------------------------------------


def parse_snapshot(serialized_chunks: list[str]) -> ListSnapshot:
    """Parse a list note's serialized command chunks into a structured snapshot.

    Iterate through the command stream to extract the section, items, their
    text, and checked state.
    """
    if not serialized_chunks:
        raise ValueError("No serialized chunks to parse.")

    commands: list[list[Any]] = json.loads(serialized_chunks[0])

    section_id = ""
    section_type = ""
    # Track items by id to pair cbx-add with docs-nestedModel
    items_by_id: dict[str, CheckboxItem] = {}
    # Track ordering for final list
    item_order: list[str] = []
    # Track checked state from cbx-p commands
    checked_map: dict[str, bool] = {}

    for cmd in commands:
        op = cmd[0]

        if op == "sct-add":
            # ["sct-add", index, section_id, type]
            section_id = cmd[2]
            section_type = cmd[3]

        elif op == "cbx-add":
            # ["cbx-add", section_id, item_id, [index]]
            item_id = cmd[2]
            items_by_id[item_id] = CheckboxItem(
                item_id=item_id,
                section_id=cmd[1],
                text="",
                checked=False,
            )
            item_order.append(item_id)

        elif op == "cbx-p":
            # ["cbx-p", section_id, item_id, [], ["cb:ck", bool]]
            item_id = cmd[2]
            props = cmd[4] if len(cmd) > 4 else []
            if len(props) >= 2 and props[0] == "cb:ck":
                checked_map[item_id] = bool(props[1])

        elif op == "docs-nestedModel" and isinstance(cmd[2], dict):
            # ["docs-nestedModel", ["text", 0, section_id, item_id], {...}]
            text = cmd[2].get("s", "")
            # Extract item_id from the address tuple
            address = cmd[1]
            if isinstance(address, list) and len(address) >= 4:
                item_id = address[3]
                if item_id in items_by_id:
                    items_by_id[item_id]["text"] = text

        elif op == "docs-mlti":
            # ["docs-mlti", [cmd1, cmd2, ...]] — recurse into batch
            inner_snapshot = _parse_commands(cmd[1], section_id, section_type)
            # Merge inner results
            if inner_snapshot["section_id"]:
                section_id = inner_snapshot["section_id"]
                section_type = inner_snapshot["section_type"]
            for item in inner_snapshot["items"]:
                iid = item["item_id"]
                if iid not in items_by_id:
                    items_by_id[iid] = item
                    item_order.append(iid)
                else:
                    if item["text"]:
                        items_by_id[iid]["text"] = item["text"]
                    if item["checked"]:
                        items_by_id[iid]["checked"] = item["checked"]

    # Apply checked state
    for item_id, checked in checked_map.items():
        if item_id in items_by_id:
            items_by_id[item_id]["checked"] = checked

    if not section_id:
        raise ValueError("Could not find section ID in snapshot commands.")

    items = [items_by_id[iid] for iid in item_order if iid in items_by_id]

    return ListSnapshot(
        section_id=section_id,
        section_type=section_type,
        items=items,
    )


def _parse_commands(
    commands: list[list[Any]],
    parent_section_id: str,
    parent_section_type: str,
) -> ListSnapshot:
    """Parse a flat list of commands (used for docs-mlti inner batches)."""
    section_id = parent_section_id
    section_type = parent_section_type
    items_by_id: dict[str, CheckboxItem] = {}
    item_order: list[str] = []

    for cmd in commands:
        op = cmd[0]

        if op == "sct-add":
            section_id = cmd[2]
            section_type = cmd[3]
        elif op == "cbx-add":
            item_id = cmd[2]
            items_by_id[item_id] = CheckboxItem(
                item_id=item_id,
                section_id=cmd[1],
                text="",
                checked=False,
            )
            item_order.append(item_id)
        elif op == "cbx-p":
            item_id = cmd[2]
            props = cmd[4] if len(cmd) > 4 else []
            if len(props) >= 2 and props[0] == "cb:ck":
                if item_id in items_by_id:
                    items_by_id[item_id]["checked"] = bool(props[1])
        elif op == "docs-nestedModel" and isinstance(cmd[2], dict):
            text = cmd[2].get("s", "")
            address = cmd[1]
            if isinstance(address, list) and len(address) >= 4:
                item_id = address[3]
                if item_id in items_by_id:
                    items_by_id[item_id]["text"] = text

    items = [items_by_id[iid] for iid in item_order if iid in items_by_id]
    return ListSnapshot(
        section_id=section_id,
        section_type=section_type,
        items=items,
    )


def parse_snapshot_from_node(node: dict[str, Any]) -> ListSnapshot:
    """Extract and parse snapshot from a Keep sync node dict.

    Convenience wrapper around ``parse_snapshot`` that navigates
    ``serverChanges.snapshot.serializedChunks`` on the node.
    """
    chunks: list[str] = (
        node.get("serverChanges", {}).get("snapshot", {}).get("serializedChunks", [])
    )
    if not chunks:
        raise ValueError("Node has no snapshot data — cannot parse list items.")
    return parse_snapshot(chunks)


# ---------------------------------------------------------------------------
# Building: intent → command arrays
# ---------------------------------------------------------------------------


def build_check_item(section_id: str, item_id: str, checked: bool) -> list[Any]:
    """Build a ``cbx-p`` command to check/uncheck a list item."""
    return ["cbx-p", section_id, item_id, [], ["cb:ck", checked]]


def build_add_checkbox(section_id: str, item_id: str, index: list[int] | None = None) -> list[Any]:
    """Build a ``cbx-add`` command to add a checkbox item."""
    return ["cbx-add", section_id, item_id, index or []]


def build_add_section(index: int, section_id: str, section_type: str) -> list[Any]:
    """Build a ``sct-add`` command to add a section."""
    return ["sct-add", index, section_id, section_type]


def build_replace_section(
    index: int,
    old_section_id: str,
    new_type: str,
    new_section_id: str,
) -> list[Any]:
    """Build a ``sct-rp`` command to convert a section type."""
    return ["sct-rp", index, old_section_id, new_type, new_section_id]


def build_item_text(section_id: str, item_id: str, text: str) -> list[Any]:
    """Build a ``docs-nestedModel`` command to set item text."""
    return [
        "docs-nestedModel",
        ["text", 0, section_id, item_id],
        {"ibi": 1, "s": text, "ty": "is"},
    ]


def build_batch(commands: list[list[Any]]) -> list[Any]:
    """Build a ``docs-mlti`` command to batch multiple commands."""
    return ["docs-mlti", commands]


# ---------------------------------------------------------------------------
# Composed builders
# ---------------------------------------------------------------------------


def build_add_list_item(
    section_id: str,
    item_id: str,
    text: str,
    index: list[int] | None = None,
) -> list[list[Any]]:
    """Build the command sequence to add a new list item with text.

    Return a list of two commands: ``cbx-add`` followed by ``docs-nestedModel``.
    """
    return [
        build_add_checkbox(section_id, item_id, index),
        build_item_text(section_id, item_id, text),
    ]


def serialize_commands(commands: list[list[Any]]) -> str:
    """Serialize a list of commands to JSON for the wire protocol."""
    return json.dumps(commands)
