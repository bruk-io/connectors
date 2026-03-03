"""Unit tests for LinkedIn domain operations."""

import pytest

from connectors.domain.linkedin.operations import (
    conversations_api_url,
    extract_profile_urn,
    messages_api_url,
    parse_conversation_urn,
    parse_profile_urn,
)


class TestParseConversationUrn:
    def test_valid_urn(self) -> None:
        urn = "urn:li:msg_conversation:(urn:li:fsd_profile:ABC123,2-thread-id)"
        assert parse_conversation_urn(urn) == urn

    def test_valid_urn_real_format(self) -> None:
        urn = (
            "urn:li:msg_conversation:"
            "(urn:li:fsd_profile:ACoAABxxxxXXXXxxxxXXXXxxxxX,"
            "2-Mzk5MDhlYmMtZjBjYy00Nzk4XzEwMA==)"
        )
        assert parse_conversation_urn(urn) == urn

    def test_strips_whitespace(self) -> None:
        urn = "urn:li:msg_conversation:(urn:li:fsd_profile:ABC,thread)"
        assert parse_conversation_urn(f"  {urn}  ") == urn

    def test_invalid_empty(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn conversation URN"):
            parse_conversation_urn("")

    def test_invalid_plain_string(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn conversation URN"):
            parse_conversation_urn("some-random-string")

    def test_invalid_wrong_urn_type(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn conversation URN"):
            parse_conversation_urn("urn:li:fsd_profile:ABC123")

    def test_invalid_missing_parens(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn conversation URN"):
            parse_conversation_urn("urn:li:msg_conversation:no-parens")


class TestParseProfileUrn:
    def test_valid_urn(self) -> None:
        urn = "urn:li:fsd_profile:ACoAABxxxxXXXXxxxxXXXXxxxxXXXXxxxxXXXXxx"
        assert parse_profile_urn(urn) == urn

    def test_strips_whitespace(self) -> None:
        urn = "urn:li:fsd_profile:ABC123"
        assert parse_profile_urn(f"  {urn}  ") == urn

    def test_invalid_empty(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn profile URN"):
            parse_profile_urn("")

    def test_invalid_wrong_urn_type(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn profile URN"):
            parse_profile_urn("urn:li:msg_conversation:(foo)")

    def test_invalid_plain_string(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn profile URN"):
            parse_profile_urn("just-a-string")


class TestExtractProfileUrn:
    def test_extracts_from_me_response(self) -> None:
        response = {
            "miniProfile": {
                "dashEntityUrn": "urn:li:fsd_profile:ACoAABxxxxXXXXxxxxXXXXxxxxXXXXxxxxXXXXxx",
                "firstName": "Test",
            }
        }
        assert (
            extract_profile_urn(response)
            == "urn:li:fsd_profile:ACoAABxxxxXXXXxxxxXXXXxxxxXXXXxxxxXXXXxx"
        )

    def test_missing_mini_profile(self) -> None:
        with pytest.raises(ValueError, match="Could not extract profile URN"):
            extract_profile_urn({})

    def test_missing_dash_entity_urn(self) -> None:
        with pytest.raises(ValueError, match="Could not extract profile URN"):
            extract_profile_urn({"miniProfile": {}})

    def test_invalid_urn_value(self) -> None:
        with pytest.raises(ValueError, match="Not a valid LinkedIn profile URN"):
            extract_profile_urn({"miniProfile": {"dashEntityUrn": "not-a-urn"}})


class TestConversationsApiUrl:
    def test_builds_url(self) -> None:
        urn = "urn:li:fsd_profile:ABC123"
        url = conversations_api_url(urn)
        assert url.startswith(
            "https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql"
        )
        assert "queryId=messengerConversations." in url
        assert "mailboxUrn:" in url

    def test_urn_is_encoded(self) -> None:
        urn = "urn:li:fsd_profile:ABC123"
        url = conversations_api_url(urn)
        assert "urn%3Ali%3Afsd_profile" in url


class TestMessagesApiUrl:
    def test_builds_url(self) -> None:
        urn = "urn:li:msg_conversation:(urn:li:fsd_profile:ABC,thread)"
        url = messages_api_url(urn)
        assert url.startswith(
            "https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql"
        )
        assert "queryId=messengerMessages." in url
        assert "conversationUrn:" in url

    def test_urn_is_encoded(self) -> None:
        urn = "urn:li:msg_conversation:(urn:li:fsd_profile:ABC,thread)"
        url = messages_api_url(urn)
        assert "urn%3Ali%3Amsg_conversation" in url
