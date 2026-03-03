"""LinkedIn domain — conversation URN validation and API URL construction."""

from connectors.domain.linkedin.operations import (
    ME_API_URL,
    conversations_api_url,
    extract_profile_urn,
    messages_api_url,
    parse_conversation_urn,
    parse_profile_urn,
)

__all__ = [
    "ME_API_URL",
    "conversations_api_url",
    "extract_profile_urn",
    "messages_api_url",
    "parse_conversation_urn",
    "parse_profile_urn",
]
