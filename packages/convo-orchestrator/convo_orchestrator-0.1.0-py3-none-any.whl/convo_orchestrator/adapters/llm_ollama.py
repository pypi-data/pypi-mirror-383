# adapters/llm_ollama.py

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib import error, request

from ..shared import AppError, Config, ErrorKind, LogBus, Result
from ..domain.llm_domain import ChatMessage, LLMClient, LLMRequest, LLMResponse, StreamCallback


class OllamaLLMClient(LLMClient):
    """
    Adapter for a local Ollama chat endpoint (`/api/chat`).

    Behavior:
        - Non-streaming `generate()` sends one POST and returns the final text.
        - Streaming `stream()` reads JSON lines and forwards incremental deltas
          to `on_delta`, concatenating them for the final `LLMResponse`.

    Configuration (via Config):
        - OLLAMA_HOST (default: "http://localhost")
        - OLLAMA_PORT (default: "11434")
        - OLLAMA_TIMEOUT_SECS (default: 60)
        - RAG_GEN_MODEL (default: "llama3.2:latest")
    """

    def __init__(self, model: Optional[str] = None, log_topic: str = "llm.ollama") -> None:
        cfg = Config.instance()
        host = cfg.get("OLLAMA_HOST", "http://localhost")
        port = cfg.get("OLLAMA_PORT", "11434")
        self._endpoint = f"{host}:{port}/api/chat"
        self._model = model or cfg.get("RAG_GEN_MODEL", "llama3.2:latest")
        self._timeout = int(cfg.get("OLLAMA_TIMEOUT_SECS", 60))
        self._log = LogBus.instance().topic(log_topic)

    # --------------------------------------------------------------------- utils

    def _to_ollama_msgs(self, msgs: List[ChatMessage]) -> List[Dict[str, str]]:
        """Convert domain chat messages to Ollama's message format."""
        return [{"role": m.role, "content": m.content} for m in msgs]

    def _post(self, payload: Dict[str, Any]):
        """Execute a POST request to the Ollama endpoint."""
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return request.urlopen(req, timeout=self._timeout)

    # ----------------------------------------------------------------- generate

    def generate(self, req: LLMRequest) -> Result[LLMResponse, AppError]:
        """
        Perform a non-streaming completion.

        Returns:
            Ok(LLMResponse) on success, Err(AppError) on failure.
        """
        body: Dict[str, Any] = {
            "model": self._model,
            "messages": self._to_ollama_msgs(req.messages),
            "options": {"temperature": req.temperature},
            "stream": False,
        }
        if req.max_tokens is not None:
            body["options"]["num_predict"] = req.max_tokens
        if req.stop:
            body["options"]["stop"] = req.stop
        if req.extra:
            body["options"].update(req.extra)

        try:
            with self._post(body) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except error.HTTPError as ex:
            err = AppError(ErrorKind.LLM_ERROR, f"Ollama HTTP error: {ex.status} {ex.reason}")
            self._log.error("Ollama HTTP error", status=getattr(ex, "status", None), reason=getattr(ex, "reason", None))
            return Result.Err(err)
        except Exception as ex:
            err = AppError(ErrorKind.LLM_ERROR, f"Ollama generate failed: {ex}")
            self._log.error("Ollama request failed", exc=err)
            return Result.Err(err)

        text = (data.get("message") or {}).get("content", "") or ""
        return Result.Ok(
            LLMResponse(
                text=text,
                model=data.get("model"),
                finish_reason="stop" if data.get("done") else None,
                usage={
                    "eval_count": data.get("eval_count"),
                    "prompt_eval_count": data.get("prompt_eval_count"),
                    "total_duration": data.get("total_duration"),
                },
                raw=data,
            )
        )

    # -------------------------------------------------------------------- stream

    def stream(self, req: LLMRequest, on_delta: StreamCallback) -> Result[LLMResponse, AppError]:
        """
        Perform a streaming completion, invoking `on_delta` for each partial chunk.

        Returns:
            Ok(LLMResponse) with the concatenated text on success,
            Err(AppError) on failure.
        """
        body: Dict[str, Any] = {
            "model": self._model,
            "messages": self._to_ollama_msgs(req.messages),
            "options": {"temperature": req.temperature},
            "stream": True,
        }
        if req.max_tokens is not None:
            body["options"]["num_predict"] = req.max_tokens
        if req.stop:
            body["options"]["stop"] = req.stop
        if req.extra:
            body["options"].update(req.extra)

        try:
            with self._post(body) as resp:
                chunks: List[str] = []
                for line in resp:
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line.decode("utf-8"))
                    except Exception:
                        # Ignore malformed JSON lines and continue streaming.
                        continue

                    msg = event.get("message", {})
                    delta = msg.get("content", "") or ""
                    if delta:
                        chunks.append(delta)
                        try:
                            on_delta(delta)
                        except Exception:
                            # Do not abort the stream if the callback misbehaves.
                            pass

                    if event.get("done"):
                        return Result.Ok(
                            LLMResponse(
                                text="".join(chunks),
                                finish_reason="stop",
                                model=event.get("model", self._model),
                                raw=event,
                            )
                        )
        except error.HTTPError as ex:
            err = AppError(ErrorKind.LLM_ERROR, f"Ollama HTTP error (stream): {ex.status} {ex.reason}")
            self._log.error("Ollama HTTP error (stream)", status=getattr(ex, "status", None), reason=getattr(ex, "reason", None))
            return Result.Err(err)
        except Exception as ex:
            err = AppError(ErrorKind.LLM_ERROR, f"Ollama stream failed: {ex}")
            self._log.error("Ollama stream failed", exc=err)
            return Result.Err(err)
