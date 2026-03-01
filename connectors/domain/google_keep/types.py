"""Google Keep domain types — mirrors the official Google Keep API schema."""

from typing import TypedDict


class TextContent(TypedDict):
    """Plain text content of a note or list item."""

    text: str


class ListItem(TypedDict):
    """Single item in a list note."""

    text: TextContent
    checked: bool
    childListItems: list[ListItem]


class ListContent(TypedDict):
    """Content of a list-type note."""

    listItems: list[ListItem]


class Section(TypedDict, total=False):
    """Union-like section: either text or list content."""

    text: TextContent
    list: ListContent


class Attachment(TypedDict):
    """File attachment on a note."""

    name: str
    mimeType: list[str]


class Note(TypedDict, total=False):
    """Google Keep note — mirrors the official API resource."""

    name: str
    title: str
    body: Section
    createTime: str
    updateTime: str
    trashTime: str
    trashed: bool
    attachments: list[Attachment]


class CheckboxItem(TypedDict):
    """Single checkbox item parsed from a list note's command snapshot."""

    item_id: str
    section_id: str
    text: str
    checked: bool


class ListSnapshot(TypedDict):
    """Parsed snapshot of a list note's command stream."""

    section_id: str
    section_type: str
    items: list[CheckboxItem]
