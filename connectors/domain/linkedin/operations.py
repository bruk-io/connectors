"""LinkedIn domain operations — pure functions, no I/O."""

import re
from typing import Any
from urllib.parse import quote

ME_API_URL = "https://www.linkedin.com/voyager/api/me"

_MESSAGES_QUERY_ID = "messengerMessages.5846eeb71c981f11e0134cb6626cc314"
_CONVERSATIONS_QUERY_ID = "messengerConversations.0d5e6781bbee71c3e51c8843c6519f48"

_CONVERSATION_URN_PATTERN = re.compile(r"^urn:li:msg_conversation:\(.+\)$")
_PROFILE_URN_PATTERN = re.compile(r"^urn:li:fsd_profile:[A-Za-z0-9_-]+$")


def parse_conversation_urn(urn: str) -> str:
    """Validate a LinkedIn conversation URN.

    Raise ValueError if the URN is not valid.
    """
    stripped = urn.strip()
    if not _CONVERSATION_URN_PATTERN.match(stripped):
        raise ValueError(
            f"Not a valid LinkedIn conversation URN: {urn}\n"
            "Expected format: urn:li:msg_conversation:(urn:li:fsd_profile:<id>,<thread_id>)"
        )
    return stripped


def parse_profile_urn(urn: str) -> str:
    """Validate a LinkedIn profile URN.

    Raise ValueError if the URN is not valid.
    """
    stripped = urn.strip()
    if not _PROFILE_URN_PATTERN.match(stripped):
        raise ValueError(
            f"Not a valid LinkedIn profile URN: {urn}\nExpected format: urn:li:fsd_profile:<id>"
        )
    return stripped


def extract_profile_urn(me_response: dict[str, Any]) -> str:
    """Extract the profile URN from a /voyager/api/me response.

    Raise ValueError if the URN cannot be found.
    """
    try:
        urn = me_response["miniProfile"]["dashEntityUrn"]
    except (KeyError, TypeError) as e:
        raise ValueError(f"Could not extract profile URN from /me response: {e}") from e
    return parse_profile_urn(urn)


def conversations_api_url(profile_urn: str) -> str:
    """Build the Voyager MessagingGraphQL URL for listing conversations."""
    encoded_urn = quote(profile_urn, safe="")
    return (
        "https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql"
        f"?queryId={_CONVERSATIONS_QUERY_ID}"
        f"&variables=(mailboxUrn:{encoded_urn})"
    )


def messages_api_url(conversation_urn: str) -> str:
    """Build the Voyager MessagingGraphQL URL for fetching messages."""
    encoded_urn = quote(conversation_urn, safe="")
    return (
        "https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql"
        f"?queryId={_MESSAGES_QUERY_ID}"
        f"&variables=(conversationUrn:{encoded_urn})"
    )
