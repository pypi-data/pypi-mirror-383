# application/rag_context_service.py

from typing import List
from ..shared import Result, AppError, LogBus
from ..domain.prompt_domain import PromptBudget


class RAGContextService:
    """
    Retrieves and fuses contextual information from lexical and vector stores
    for retrieval-augmented generation (RAG) workflows.

    This service performs multi-source retrieval, merges scores across
    backends, deduplicates results by document ID, and builds a simple
    human-readable context snippet.

    Dependencies:
        - Lexical store implementing `search(query, limit) -> Result[List[RetrievalItem], AppError]`
        - Vector store implementing `search(query_vector, limit) -> Result[List[RetrievalItem], AppError]`
        - Text encoder implementing `embed(text) -> List[float]`
        - LogBus for structured logging
    """

    def __init__(self, lexical, vector, encoder, log_topic: str = "app.ragctx"):
        """
        Initialize the RAG context service.

        Args:
            lexical: Lexical search adapter (BM25, PostgreSQL full-text, etc.).
            vector: Vector search adapter (Qdrant, Chroma, etc.).
            encoder: Text encoder used to embed the query for vector search.
            log_topic: LogBus topic name for logging context operations.
        """
        self._lex = lexical
        self._vec = vector
        self._enc = encoder
        self._log = LogBus.instance().topic(log_topic)

    def fetch_context(self, query: str, k: int, budget: int) -> Result[str, AppError]:
        """
        Retrieve a textual context snippet relevant to the given query.

        Strategy:
            1) Query both lexical and vector stores.
            2) Merge and deduplicate results by document ID.
            3) Combine name and description metadata to produce a simple text block.
            4) The final token-level truncation will be handled by PromptBuilder.

        Args:
            query: User or system query text.
            k: Number of top-ranked items to return.
            budget: Token or length budget (used only for downstream truncation).

        Returns:
            Result containing the concatenated textual context snippet or an AppError.
        """
        # 1) Lexical retrieval
        lres = self._lex.search(query, limit=max(3, k)).unwrap_or([])

        # 2) Vector retrieval
        vres = self._vec.search(self._enc.embed(query), limit=max(3, k)).unwrap_or([])

        # 3) Merge metadata and scores by document ID
        meta = {}
        for h in lres:
            meta[h.doc_id] = h.metadata
        for h in vres:
            meta.setdefault(h.doc_id, h.metadata)

        scores = {}
        for h in lres:
            scores[h.doc_id] = scores.get(h.doc_id, 0.0) + float(getattr(h, "score", 0.0) or 0.0)
        for h in vres:
            scores[h.doc_id] = scores.get(h.doc_id, 0.0) + float(getattr(h, "score", 0.0) or 0.0)

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]

        # 4) Build a human-readable text snippet
        chunks: List[str] = []
        for doc_id, _ in top:
            m = meta.get(doc_id) or {}
            name = m.get("name") or m.get("title") or f"doc:{doc_id}"
            desc = m.get("description") or ""
            chunks.append(f"- {name}\n  {desc}".strip())

        ctx = "\n".join(chunks).strip()

        self._log.debug(
            "Fetched RAG context.",
            query=query,
            results=len(top),
            context_preview=ctx[:120],
        )

        # Final truncation to token budget will be applied downstream by PromptBuilder
        return Result.Ok(ctx)
