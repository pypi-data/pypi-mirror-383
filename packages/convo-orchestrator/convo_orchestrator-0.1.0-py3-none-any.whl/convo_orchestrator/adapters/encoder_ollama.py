# adapters/encoder_ollama.py
from __future__ import annotations

import json
from typing import List
from urllib import error, request

from ..shared import AppError, LogBus, Result
from ..domain.rag_domain import TextEncoder


class OllamaEncoder(TextEncoder):
    """
    Text encoder backed by a local Ollama embeddings endpoint.

    Endpoint:
        POST /api/embeddings
        Payload: {"model": "<model-name>", "prompt": "<text>"}
        Response: {"embedding": [float, ...]}

    Notes:
        - `embed()` wraps `encode()` for a single string and raises on failure,
          matching the TextEncoder protocol semantics used elsewhere.
        - `encode()` returns a `Result` to propagate recoverable errors upstream.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text:latest",
        endpoint: str = "http://localhost:11434/api/embeddings",
        log_topic: str = "rag.encoder.ollama",
    ) -> None:
        self._model = model
        self._endpoint = endpoint
        self._log = LogBus.instance().topic(log_topic)

    def embed(self, text: str) -> List[float]:
        """
        Encode a single text into a dense vector.

        Raises:
            AppError: If the underlying encode call fails.
        """
        res = self.encode([text])
        if res.is_err():
            raise res.unwrap_err()
        vec = res.unwrap()[0]
        if not vec:
            raise AppError.embedding(
                f"Ollama returned empty embedding (model={self._model}). "
                "Model may not be ready or not an embedding model."
            )
        return vec

    def encode(self, texts: List[str]) -> Result[List[List[float]], AppError]:
        """
        Encode multiple texts into dense vectors.

        Args:
            texts: List of input strings.

        Returns:
            Ok(list of embeddings) on success, Err(AppError) on failure.
        """
        all_vecs: List[List[float]] = []

        for t in texts:
            payload = json.dumps({"model": self._model, "prompt": t}).encode("utf-8")
            req = request.Request(
                self._endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=60) as resp:
                    data_raw = resp.read().decode("utf-8") or "{}"
                    data = json.loads(data_raw)

                    # Expect: {"embedding": [...]}
                    emb = data.get("embedding")
                    if emb is None:
                        return Result.Err(AppError.embedding(f"Ollama unexpected payload: {data_raw}"))

                    emb_list = [float(x) for x in emb]
                    if not emb_list:
                        return Result.Err(
                            AppError.embedding(f"Ollama returned empty embedding (model={self._model})")
                        )
                    all_vecs.append(emb_list)

            except error.URLError as ex:
                err = AppError.embedding(f"Failed to reach Ollama at {self._endpoint}: {ex}")
                self._log.error("ollama connection error", exc=err)
                return Result.Err(err)
            except Exception as ex:
                err = AppError.embedding(str(ex))
                self._log.error("ollama encode failed", exc=err)
                return Result.Err(err)

        self._log.debug(lambda: f"encoded {len(all_vecs)} texts via Ollama ({self._model})")
        return Result.Ok(all_vecs)
