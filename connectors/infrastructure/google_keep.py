"""Google Keep API client — browser-authenticated sync protocol.

Google Keep uses a single sync endpoint (POST /notes/v1/changes) for all
operations. Notes are represented as "nodes" in a tree (parentId: "root").
Auth requires browser cookies plus a SAPISIDHASH authorization header
derived from the SAPISID cookie.
"""

import hashlib
import json
import logging
import random
import time
from typing import Any

from connectors.browser_auth import BrowserSession, SupportedBrowser
from connectors.domain.google_keep.commands import (
    build_check_item as _build_check_item,
)
from connectors.domain.google_keep.commands import (
    parse_snapshot_from_node,
    serialize_commands,
)

logger = logging.getLogger(__name__)

_BASE_URL = "https://notes-pa.clients6.google.com/notes/v1"
_API_KEY = "AIzaSyDE7NHMUZfMoJVu-YNkK-7AXFSuL1Q9gKE"
_ORIGIN = "https://keep.google.com"
_EPOCH = "1970-01-01T00:00:00.000Z"
_CLIENT_VERSION = {"major": "3", "minor": "3", "build": "0", "revision": "370"}
_CAPABILITY_TYPES = [
    "EC",
    "TR",
    "SH",
    "LB",
    "RB",
    "DR",
    "AN",
    "PI",
    "EX",
    "IN",
    "SNB",
    "CO",
    "MI",
    "NC",
    "CL",
    "IN",
]
_CAPABILITIES = [{"type": t} for t in _CAPABILITY_TYPES]


def _generate_sapisidhash(sapisid: str, origin: str) -> str:
    """Generate SAPISIDHASH authorization value from SAPISID cookie.

    Formula: SHA1(timestamp + " " + SAPISID + " " + origin)
    """
    timestamp = int(time.time())
    token = f"{timestamp} {sapisid} {origin}"
    hash_value = hashlib.sha1(token.encode()).hexdigest()
    pair = f"{timestamp}_{hash_value}"
    return f"SAPISIDHASH {pair} SAPISID1PHASH {pair} SAPISID3PHASH {pair}"


def _generate_node_id() -> str:
    """Generate a client-side node ID in Keep's format: timestamp.random."""
    ts = int(time.time() * 1000)
    rand = random.randint(1000000000, 9999999999)
    return f"{ts}.{rand}"


def _generate_request_id() -> str:
    """Generate a request ID in Keep's format."""
    rand_suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=12))
    ts = int(time.time() * 1000)
    return f"request.{rand_suffix}.{ts}"


def _generate_session_id() -> str:
    """Generate a client session ID in Keep's format."""
    ts = int(time.time() * 1000)
    rand = random.randint(1000000000, 9999999999)
    return f"s--{ts}--{rand}"


def _build_request_header(session_id: str) -> dict[str, Any]:
    """Build the requestHeader envelope for a changes request."""
    return {
        "requestId": _generate_request_id(),
        "clientVersion": _CLIENT_VERSION,
        "clientPlatform": "WEB",
        "capabilities": _CAPABILITIES,
        "clientSessionId": session_id,
        "clientLocale": "en-US",
    }


def _create_session() -> tuple[BrowserSession, str]:
    """Create an authenticated BrowserSession for Google Keep.

    Return the session and the SAPISID cookie value.
    """
    session = BrowserSession(browser=SupportedBrowser.ARC, domain_filter="google.com")
    cookies = session.get_cookies_dict()

    sapisid = cookies.get("SAPISID")
    if not sapisid:
        raise RuntimeError("SAPISID cookie not found. Log in to Google Keep in your browser first.")

    auth_header = _generate_sapisidhash(sapisid, _ORIGIN)
    session.update_headers(
        {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "X-Origin": _ORIGIN,
            "X-Referer": _ORIGIN,
            "X-Goog-Authuser": "0",
            "X-Goog-Encode-Response-If-Executable": "base64",
            "X-Javascript-User-Agent": "google-api-javascript-client/1.1.0",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    return session, sapisid


def _sync(
    session: BrowserSession,
    nodes: list[dict[str, Any]],
    target_version: str = "",
) -> dict[str, Any]:
    """Execute a sync request against the changes endpoint.

    Send local node changes and receive server-side updates.
    Empty nodes with a target_version performs a pull-only sync.
    Empty target_version triggers an initial full sync.
    """
    client_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    session_id = _generate_session_id()

    payload: dict[str, Any] = {
        "clientTimestamp": client_timestamp,
        "nodes": nodes,
        "requestHeader": _build_request_header(session_id),
    }
    if target_version:
        payload["targetVersion"] = target_version

    url = f"{_BASE_URL}/changes?alt=json&key={_API_KEY}"
    response = session.post(url, content=json.dumps(payload))
    response.raise_for_status()
    result: dict[str, Any] = response.json()
    return result


def _full_sync(session: BrowserSession) -> dict[str, Any]:
    """Pull-only sync to get server state and version."""
    return _sync(session, nodes=[])


def _find_node(result: dict[str, Any], note_id: str) -> dict[str, Any]:
    """Find a root note node by client ID or serverId."""
    nodes: list[dict[str, Any]] = result.get("nodes", [])
    for node in nodes:
        if node.get("parentId") != "root":
            continue
        if node.get("id") == note_id or node.get("serverId") == note_id:
            return node
    raise ValueError(f"Note not found: {note_id}")


def list_notes() -> str:
    """List all notes via initial full sync (no targetVersion)."""
    session, _ = _create_session()
    result = _full_sync(session)
    return json.dumps(result, indent=2)


def get_note(note_id: str) -> str:
    """Fetch a note by syncing and filtering by ID.

    Keep's API doesn't support single-note fetch — we sync
    all changes and filter client-side.
    """
    session, _ = _create_session()
    result = _full_sync(session)
    node = _find_node(result, note_id)
    return json.dumps(node, indent=2)


def create_note(title: str, content: str) -> str:
    """Create a new text note."""
    session, _ = _create_session()

    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    node_id = _generate_node_id()

    note_node: dict[str, Any] = {
        "id": node_id,
        "kind": "notes#node",
        "parentId": "root",
        "type": "NOTE",
        "timestamps": {
            "kind": "notes#timestamps",
            "created": now,
            "deleted": _EPOCH,
            "trashed": _EPOCH,
            "updated": now,
            "userEdited": now,
        },
        "title": title,
        "isArchived": False,
        "isPinned": False,
        "sortValue": int(time.time()),
        "baseVersion": "0",
        "nodeSettings": {
            "newListItemPlacement": "BOTTOM",
            "checkedListItemsPolicy": "GRAVEYARD",
            "graveyardState": "EXPANDED",
        },
    }

    body_node_id = _generate_node_id()
    body_node: dict[str, Any] = {
        "id": body_node_id,
        "kind": "notes#node",
        "parentId": node_id,
        "type": "LIST_ITEM",
        "timestamps": {
            "kind": "notes#timestamps",
            "created": now,
            "deleted": _EPOCH,
            "trashed": _EPOCH,
            "updated": now,
            "userEdited": now,
        },
        "text": content,
        "baseVersion": "0",
    }

    result = _sync(session, nodes=[note_node, body_node])
    return json.dumps(result, indent=2)


def create_list(title: str, items: list[str]) -> str:
    """Create a new checklist note with items."""
    session, _ = _create_session()

    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    node_id = _generate_node_id()

    list_node: dict[str, Any] = {
        "id": node_id,
        "kind": "notes#node",
        "parentId": "root",
        "type": "LIST",
        "timestamps": {
            "kind": "notes#timestamps",
            "created": now,
            "deleted": _EPOCH,
            "trashed": _EPOCH,
            "updated": now,
            "userEdited": now,
        },
        "title": title,
        "isArchived": False,
        "isPinned": False,
        "sortValue": int(time.time()),
        "baseVersion": "0",
        "nodeSettings": {
            "newListItemPlacement": "BOTTOM",
            "checkedListItemsPolicy": "GRAVEYARD",
            "graveyardState": "EXPANDED",
        },
    }

    item_nodes: list[dict[str, Any]] = []
    for i, item_text in enumerate(items):
        item_node: dict[str, Any] = {
            "id": _generate_node_id(),
            "kind": "notes#node",
            "parentId": node_id,
            "type": "LIST_ITEM",
            "timestamps": {
                "kind": "notes#timestamps",
                "created": now,
                "deleted": _EPOCH,
                "trashed": _EPOCH,
                "updated": now,
                "userEdited": now,
            },
            "text": item_text,
            "checked": False,
            "baseVersion": "0",
            "sortValue": str(i),
        }
        item_nodes.append(item_node)

    result = _sync(session, nodes=[list_node, *item_nodes])
    return json.dumps(result, indent=2)


def check_item(note_id: str, item_text: str, checked: bool = True) -> str:
    """Check or uncheck a list item by matching its text."""
    session, _ = _create_session()
    sync_result = _full_sync(session)
    version: str = sync_result.get("toVersion", "")
    node = _find_node(sync_result, note_id)

    snapshot = parse_snapshot_from_node(node)
    item_map = {item["text"]: item for item in snapshot["items"]}

    if item_text not in item_map:
        available = ", ".join(item_map.keys())
        raise ValueError(f"Item '{item_text}' not found. Available items: {available}")

    matched = item_map[item_text]
    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    session_id = str(random.randint(1000000000000000000, 9999999999999999999))

    cbx_command = serialize_commands(
        [_build_check_item(matched["section_id"], matched["item_id"], checked)]
    )

    node["timestamps"]["updated"] = now
    node["timestamps"]["userEdited"] = now
    node["clientChanges"] = {
        "clientRevision": "1",
        "commandBundles": [
            {
                "sessionId": session_id,
                "requestId": "0",
                "serializedCommands": cbx_command,
            }
        ],
    }

    result = _sync(session, nodes=[node], target_version=version)
    return json.dumps(result, indent=2)


def _update_note(
    session: BrowserSession,
    note_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Fetch a note, apply updates, and sync the full node back.

    Perform a full sync to get the current version and node state,
    apply the updates to the node, and send it back.
    """
    sync_result = _full_sync(session)
    version: str = sync_result.get("toVersion", "")
    node = _find_node(sync_result, note_id)

    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    node["timestamps"]["updated"] = now
    node.update(updates)

    return _sync(session, nodes=[node], target_version=version)


def delete_note(note_id: str) -> str:
    """Delete (trash) a note by ID."""
    session, _ = _create_session()

    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    result = _update_note(
        session,
        note_id,
        {
            "trashState": 1,
            "timestamps": {
                "kind": "notes#timestamps",
                "updated": now,
                "trashed": now,
            },
        },
    )
    return json.dumps(result, indent=2)


def pin_note(note_id: str, pinned: bool = True) -> str:
    """Pin or unpin a note by ID."""
    session, _ = _create_session()
    result = _update_note(session, note_id, {"isPinned": pinned})
    return json.dumps(result, indent=2)


def download_attachment(note_id: str, attachment_id: str) -> bytes:
    """Download a note attachment."""
    raise NotImplementedError("Google Keep download_attachment: endpoint discovery pending")
