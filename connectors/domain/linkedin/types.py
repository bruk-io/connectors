"""LinkedIn domain types."""

from typing import TypedDict


class Message(TypedDict):
    """A LinkedIn message."""

    sender_name: str
    body: str
    timestamp: int


class Conversation(TypedDict):
    """A LinkedIn conversation thread."""

    conversation_id: str
    participants: list[str]
    messages: list[Message]
