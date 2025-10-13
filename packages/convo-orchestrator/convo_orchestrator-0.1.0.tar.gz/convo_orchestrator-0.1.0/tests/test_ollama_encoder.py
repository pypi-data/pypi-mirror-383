# tests/test_ollama_encoder.py
from __future__ import annotations

import math
import os
import pytest

from convo_orchestrator.adapters.encoder_ollama import OllamaEncoder


@pytest.mark.integration
def test_ollama_encoder_basic():
    """
    Integration test for the OllamaEncoder.

    Ensures that embeddings are successfully generated for simple texts,
    with correct dimensionality and finite float values.
    """
    model = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")
    endpoint = f"http://localhost:{os.getenv('OLLAMA_PORT', '11434')}/api/embeddings"

    enc = OllamaEncoder(model=model, endpoint=endpoint)

    texts = ["hello world", "hello world!"]
    res = enc.encode(texts)

    assert res.is_ok(), f"encode failed: {res}"
    vecs = res.unwrap()

    # Expect two embeddings
    assert len(vecs) == 2

    # Embedding dimensionality should be reasonable
    dim = len(vecs[0])
    assert dim > 16, "embedding dimension appears unexpectedly small"

    # Ensure all vector elements are finite floats
    assert all(math.isfinite(x) for x in vecs[0])
