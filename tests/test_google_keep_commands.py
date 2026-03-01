"""Unit tests for Google Keep command protocol parsing and building."""

import json

import pytest

from connectors.domain.google_keep.commands import (
    build_add_checkbox,
    build_add_list_item,
    build_add_section,
    build_batch,
    build_check_item,
    build_item_text,
    build_replace_section,
    parse_snapshot,
    parse_snapshot_from_node,
    serialize_commands,
)

# ---------------------------------------------------------------------------
# Fixtures: realistic command streams captured from network traffic
# ---------------------------------------------------------------------------

_SEC1 = "section-001"
_SEC2 = "section-002"


def _text_cmd(sec: str, item: str, text: str) -> list[object]:
    """Build a docs-nestedModel fixture command."""
    return ["docs-nestedModel", ["text", 0, sec, item], {"ibi": 1, "s": text, "ty": "is"}]


_BASIC_LIST_COMMANDS: list[list[object]] = [
    ["sct-add", 0, _SEC1, "cbx"],
    ["cbx-add", _SEC1, "item-aaa", [0]],
    _text_cmd(_SEC1, "item-aaa", "Milk"),
    ["cbx-add", _SEC1, "item-bbb", [1]],
    _text_cmd(_SEC1, "item-bbb", "Eggs"),
    ["cbx-add", _SEC1, "item-ccc", [2]],
    _text_cmd(_SEC1, "item-ccc", "Butter"),
]

_LIST_WITH_CHECKED: list[list[object]] = [
    ["sct-add", 0, _SEC2, "cbx"],
    ["cbx-add", _SEC2, "item-111", [0]],
    _text_cmd(_SEC2, "item-111", "Done task"),
    ["cbx-p", _SEC2, "item-111", [], ["cb:ck", True]],
    ["cbx-add", _SEC2, "item-222", [1]],
    _text_cmd(_SEC2, "item-222", "Open task"),
]


def _serialize(commands: list[list[object]]) -> list[str]:
    """Wrap commands into the serializedChunks format."""
    return [json.dumps(commands)]


# ---------------------------------------------------------------------------
# parse_snapshot
# ---------------------------------------------------------------------------


class TestParseSnapshot:
    def test_basic_list_items(self) -> None:
        snapshot = parse_snapshot(_serialize(_BASIC_LIST_COMMANDS))
        assert snapshot["section_id"] == "section-001"
        assert snapshot["section_type"] == "cbx"
        assert len(snapshot["items"]) == 3
        assert snapshot["items"][0]["text"] == "Milk"
        assert snapshot["items"][1]["text"] == "Eggs"
        assert snapshot["items"][2]["text"] == "Butter"

    def test_all_items_unchecked_by_default(self) -> None:
        snapshot = parse_snapshot(_serialize(_BASIC_LIST_COMMANDS))
        for item in snapshot["items"]:
            assert item["checked"] is False

    def test_checked_state_applied(self) -> None:
        snapshot = parse_snapshot(_serialize(_LIST_WITH_CHECKED))
        assert snapshot["items"][0]["text"] == "Done task"
        assert snapshot["items"][0]["checked"] is True
        assert snapshot["items"][1]["text"] == "Open task"
        assert snapshot["items"][1]["checked"] is False

    def test_item_ids_preserved(self) -> None:
        snapshot = parse_snapshot(_serialize(_BASIC_LIST_COMMANDS))
        assert snapshot["items"][0]["item_id"] == "item-aaa"
        assert snapshot["items"][1]["item_id"] == "item-bbb"
        assert snapshot["items"][2]["item_id"] == "item-ccc"

    def test_item_section_ids_preserved(self) -> None:
        snapshot = parse_snapshot(_serialize(_BASIC_LIST_COMMANDS))
        for item in snapshot["items"]:
            assert item["section_id"] == "section-001"

    def test_empty_chunks_raises(self) -> None:
        with pytest.raises(ValueError, match="No serialized chunks"):
            parse_snapshot([])

    def test_no_section_raises(self) -> None:
        commands: list[list[object]] = [
            ["cbx-add", "sec", "item", [0]],
        ]
        with pytest.raises(ValueError, match="Could not find section ID"):
            parse_snapshot(_serialize(commands))

    def test_docs_mlti_batch(self) -> None:
        commands: list[list[object]] = [
            ["sct-add", 0, "sec-batch", "cbx"],
            [
                "docs-mlti",
                [
                    ["cbx-add", "sec-batch", "b-item-1", [0]],
                    [
                        "docs-nestedModel",
                        ["text", 0, "sec-batch", "b-item-1"],
                        {"ibi": 1, "s": "Batched", "ty": "is"},
                    ],
                ],
            ],
        ]
        snapshot = parse_snapshot(_serialize(commands))
        assert len(snapshot["items"]) == 1
        assert snapshot["items"][0]["text"] == "Batched"

    def test_single_item_list(self) -> None:
        commands: list[list[object]] = [
            ["sct-add", 0, "sec-solo", "cbx"],
            ["cbx-add", "sec-solo", "solo-item", [0]],
            [
                "docs-nestedModel",
                ["text", 0, "sec-solo", "solo-item"],
                {"ibi": 1, "s": "Only item", "ty": "is"},
            ],
        ]
        snapshot = parse_snapshot(_serialize(commands))
        assert len(snapshot["items"]) == 1
        assert snapshot["items"][0]["text"] == "Only item"

    def test_item_with_empty_text(self) -> None:
        commands: list[list[object]] = [
            ["sct-add", 0, "sec-empty", "cbx"],
            ["cbx-add", "sec-empty", "empty-item", [0]],
            [
                "docs-nestedModel",
                ["text", 0, "sec-empty", "empty-item"],
                {"ibi": 1, "s": "", "ty": "is"},
            ],
        ]
        snapshot = parse_snapshot(_serialize(commands))
        assert snapshot["items"][0]["text"] == ""


# ---------------------------------------------------------------------------
# parse_snapshot_from_node
# ---------------------------------------------------------------------------


class TestParseSnapshotFromNode:
    def test_extracts_from_node_dict(self) -> None:
        node = {
            "serverChanges": {
                "snapshot": {
                    "serializedChunks": _serialize(_BASIC_LIST_COMMANDS),
                }
            }
        }
        snapshot = parse_snapshot_from_node(node)
        assert snapshot["section_id"] == "section-001"
        assert len(snapshot["items"]) == 3

    def test_missing_snapshot_raises(self) -> None:
        with pytest.raises(ValueError, match="no snapshot data"):
            parse_snapshot_from_node({})

    def test_empty_chunks_raises(self) -> None:
        node = {"serverChanges": {"snapshot": {"serializedChunks": []}}}
        with pytest.raises(ValueError, match="no snapshot data"):
            parse_snapshot_from_node(node)


# ---------------------------------------------------------------------------
# build_check_item
# ---------------------------------------------------------------------------


class TestBuildCheckItem:
    def test_check(self) -> None:
        cmd = build_check_item("sec-1", "item-1", True)
        assert cmd == ["cbx-p", "sec-1", "item-1", [], ["cb:ck", True]]

    def test_uncheck(self) -> None:
        cmd = build_check_item("sec-1", "item-1", False)
        assert cmd == ["cbx-p", "sec-1", "item-1", [], ["cb:ck", False]]


# ---------------------------------------------------------------------------
# build_add_checkbox
# ---------------------------------------------------------------------------


class TestBuildAddCheckbox:
    def test_with_index(self) -> None:
        cmd = build_add_checkbox("sec-1", "new-item", [0])
        assert cmd == ["cbx-add", "sec-1", "new-item", [0]]

    def test_without_index(self) -> None:
        cmd = build_add_checkbox("sec-1", "new-item")
        assert cmd == ["cbx-add", "sec-1", "new-item", []]


# ---------------------------------------------------------------------------
# build_add_section
# ---------------------------------------------------------------------------


class TestBuildAddSection:
    def test_checkbox_section(self) -> None:
        cmd = build_add_section(0, "sec-new", "cbx")
        assert cmd == ["sct-add", 0, "sec-new", "cbx"]

    def test_text_section(self) -> None:
        cmd = build_add_section(1, "sec-txt", "txt")
        assert cmd == ["sct-add", 1, "sec-txt", "txt"]


# ---------------------------------------------------------------------------
# build_replace_section
# ---------------------------------------------------------------------------


class TestBuildReplaceSection:
    def test_replace(self) -> None:
        cmd = build_replace_section(0, "old-sec", "cbx", "new-sec")
        assert cmd == ["sct-rp", 0, "old-sec", "cbx", "new-sec"]


# ---------------------------------------------------------------------------
# build_item_text
# ---------------------------------------------------------------------------


class TestBuildItemText:
    def test_sets_text(self) -> None:
        cmd = build_item_text("sec-1", "item-1", "Hello")
        assert cmd == [
            "docs-nestedModel",
            ["text", 0, "sec-1", "item-1"],
            {"ibi": 1, "s": "Hello", "ty": "is"},
        ]


# ---------------------------------------------------------------------------
# build_batch
# ---------------------------------------------------------------------------


class TestBuildBatch:
    def test_wraps_commands(self) -> None:
        cmds = [
            ["cbx-add", "sec", "item", []],
            ["cbx-p", "sec", "item", [], ["cb:ck", True]],
        ]
        batch = build_batch(cmds)
        assert batch[0] == "docs-mlti"
        assert batch[1] == cmds


# ---------------------------------------------------------------------------
# build_add_list_item (composed)
# ---------------------------------------------------------------------------


class TestBuildAddListItem:
    def test_returns_two_commands(self) -> None:
        cmds = build_add_list_item("sec-1", "new-item", "Buy milk")
        assert len(cmds) == 2
        assert cmds[0][0] == "cbx-add"
        assert cmds[1][0] == "docs-nestedModel"

    def test_command_contents(self) -> None:
        cmds = build_add_list_item("sec-1", "new-item", "Buy milk", [3])
        assert cmds[0] == ["cbx-add", "sec-1", "new-item", [3]]
        assert cmds[1][2]["s"] == "Buy milk"


# ---------------------------------------------------------------------------
# serialize_commands
# ---------------------------------------------------------------------------


class TestSerializeCommands:
    def test_serializes_to_json(self) -> None:
        cmds = [["cbx-p", "sec", "item", [], ["cb:ck", True]]]
        result = serialize_commands(cmds)
        assert json.loads(result) == cmds

    def test_empty_list(self) -> None:
        assert serialize_commands([]) == "[]"
