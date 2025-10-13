# domain/chat_domain.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol

from ..shared import Result, AppError


"""
Chat domain entities and interfaces.

This module defines the core DTOs and repository protocols used for managing
chat conversations, messages, and summaries within the domain layer.
All interfaces return `Result` types to ensure explicit error handling.
"""


@dataclass
class ChatMessageDTO:
    """
    Represents a persisted chat message within a conversation.

    Attributes:
        id: Unique identifier of the message.
        conversation_id: ID of the conversation this message belongs to.
        role: Role of the sender — typically "user", "assistant", or "system".
        content: Message text content.
        created_at: Timestamp (epoch seconds) when the message was created.
        token_count: Optional number of tokens consumed by this message.
        meta: Optional metadata dictionary for backend or adapter-specific info.
        seq: Optional sequence number indicating message order.
    """
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: float
    token_count: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None
    seq: Optional[int] = None


@dataclass
class ConversationSummaryDTO:
    """
    Represents a persisted summary of a conversation up to a given sequence number.

    Attributes:
        id: Unique identifier of the summary entry.
        conversation_id: Conversation this summary belongs to.
        summary_text: Generated summary text content.
        upto_seq: Sequence number of the last message covered by this summary.
        created_at: Timestamp (epoch seconds) when the summary was created.
        token_count: Optional number of tokens used in the summary.
        meta: Optional metadata dictionary for backend or adapter-specific info.
    """
    id: str
    conversation_id: str
    summary_text: str
    upto_seq: int
    created_at: float
    token_count: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


class ConversationRepository(Protocol):
    """
    Interface for persistent storage of chat messages and summaries.

    Methods:
        insert_message(msg) -> Result[ChatMessageDTO, AppError]
            Persists a new chat message.
        list_messages_since(conversation_id, after_seq, limit) -> Result[List[ChatMessageDTO], AppError]
            Retrieves all messages after a given sequence number.
        list_recent_messages(conversation_id, limit) -> Result[List[ChatMessageDTO], AppError]
            Retrieves the most recent messages.
        latest_summary(conversation_id) -> Result[Optional[ConversationSummaryDTO], AppError]
            Fetches the latest stored summary for the conversation.
        append_summary(s) -> Result[ConversationSummaryDTO, AppError]
            Appends a new conversation summary entry.
        last_seq(conversation_id) -> Result[int, AppError]
            Returns the highest message sequence number in the conversation.
    """
    def insert_message(self, msg: ChatMessageDTO) -> Result[ChatMessageDTO, AppError]: ...
    def list_messages_since(self, conversation_id: str, after_seq: int, limit: int = 500) -> Result[List[ChatMessageDTO], AppError]: ...
    def list_recent_messages(self, conversation_id: str, limit: int = 100) -> Result[List[ChatMessageDTO], AppError]: ...
    def latest_summary(self, conversation_id: str) -> Result[Optional[ConversationSummaryDTO], AppError]: ...
    def append_summary(self, s: ConversationSummaryDTO) -> Result[ConversationSummaryDTO, AppError]: ...
    def last_seq(self, conversation_id: str) -> Result[int, AppError]: ...


class TokenCounter(Protocol):
    """
    Interface for token counting utilities used by summarization and budgeting.

    Methods:
        count(text) -> int
            Counts tokens in a single text string.
        count_messages(messages) -> int
            Counts tokens across a sequence of message dictionaries.
    """
    def count(self, text: str) -> int: ...
    def count_messages(self, messages: Iterable[Dict[str, str]]) -> int: ...
