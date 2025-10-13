# domain/llm_domain.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol

from ..shared import Result, AppError


"""
LLM-related domain types and interfaces.

This module defines the canonical message, request, and response structures
for large language model (LLM) operations. It also provides a minimal
protocol interface (`LLMClient`) to standardize model integration.
"""


@dataclass
class ChatMessage:
    """
    Represents a single message in a chat conversation.

    Attributes:
        role: Message role — expected values are "system", "user", or "assistant".
        content: Message text content.
    """
    role: str
    content: str


@dataclass
class LLMRequest:
    """
    Structured input request for an LLM model.

    Attributes:
        messages: Ordered list of chat messages forming the model context.
        temperature: Sampling temperature (default: 0.2).
        max_tokens: Optional limit for generated tokens.
        stop: Optional list of stop sequences.
        extra: Arbitrary model-specific parameters or metadata.
    """
    messages: List[ChatMessage]
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """
    Standardized model output returned by an LLM.

    Attributes:
        text: Primary generated text output.
        finish_reason: Optional reason for generation stop (e.g., "stop", "length").
        usage: Optional token usage statistics, if provided by the backend.
        model: Optional model name or identifier.
        raw: Optional raw provider response for debugging or auditing.
    """
    text: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


StreamCallback = Callable[[str], None]


class LLMClient(Protocol):
    """
    Abstract interface for any LLM backend adapter.

    Implementations should translate standardized `LLMRequest` objects into
    actual model invocations and return a wrapped `LLMResponse`.

    Methods:
        generate(req: LLMRequest) -> Result[LLMResponse, AppError]
            Performs a full, non-streaming completion.

        stream(req: LLMRequest, on_delta: StreamCallback) -> Result[LLMResponse, AppError]
            Performs a streaming completion, calling `on_delta` with each partial token.
    """
    def generate(self, req: LLMRequest) -> Result[LLMResponse, AppError]: ...
    def stream(self, req: LLMRequest, on_delta: StreamCallback) -> Result[LLMResponse, AppError]: ...
