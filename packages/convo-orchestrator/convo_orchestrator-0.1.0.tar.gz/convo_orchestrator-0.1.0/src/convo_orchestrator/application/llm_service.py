#application/llm_service.py
from __future__ import annotations
from typing import List, Optional, Dict, Any

from ..shared import Result, AppError, LogBus
from ..domain.llm_domain import LLMClient, ChatMessage, LLMRequest, LLMResponse

class LLMService:
    """
    High-level orchestrator for prompt construction and LLM calls.
    Uses the configured LLMClient (Ollama, OpenAI, etc.).
    """
    def __init__(self, client: LLMClient, system_prompt: Optional[str] = None, log_topic: str = "app.llm") -> None:
        self._cli = client
        self._system_prompt = system_prompt or "You are a helpful assistant."
        self._log = LogBus.instance().topic(log_topic)

    def _build_messages(self, user_text: str, context: Optional[List[str]] = None) -> List[ChatMessage]:
        msgs = [ChatMessage(role="system", content=self._system_prompt)]
        if context:
            ctx = "\n".join(context)
            msgs.append(ChatMessage(role="system", content=f"Relevant context:\n{ctx}"))
        msgs.append(ChatMessage(role="user", content=user_text))
        return msgs

    def ask(
        self,
        user_text: str,
        context: Optional[List[str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Result[LLMResponse, AppError]:
        """Performs a single completion request."""
        req = LLMRequest(
            messages=self._build_messages(user_text, context),
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            extra=extra or {},
        )
        self._log.debug(lambda: f"LLMService.ask model={getattr(self._cli, '_model', 'unknown')} temp={temperature}")
        return self._cli.generate(req)

    def ask_stream(
        self,
        user_text: str,
        on_delta,
        context: Optional[List[str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Result[LLMResponse, AppError]:
        """Streams partial output through a callback."""
        req = LLMRequest(
            messages=self._build_messages(user_text, context),
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            extra=extra or {},
        )
        self._log.debug(lambda: "LLMService.ask_stream invoked")
        return self._cli.stream(req, on_delta)
