# domain/rag_domain.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple
import math

# Reuse our shared primitives (same style as events.py)
from ..shared import Result, AppError, LogBus


# ------------------------------
# Domain types
# ------------------------------

@dataclass(frozen=True)
class IndexedDoc:
    """Canonical record used for both lexical and vector indices."""
    doc_id: str
    text_index: str
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass(frozen=True)
class QuerySlot:
    """Single intent segment extracted from a chat message."""
    text: str
    hints: Dict[str, Any]


@dataclass(frozen=True)
class RetrievalItem:
    """Candidate with a calibrated-like score in [0,1] and lightweight metadata."""
    doc_id: str
    score: float
    metadata: Dict[str, Any]


class RetrievalDecision:
    EXACT = "EXACT"          # confident exact(s)
    CANDIDATES = "CANDIDATES"  # plausible top-N
    NONE = "NONE"            # confident absence


@dataclass(frozen=True)
class RetrievalResult:
    """Aggregated retrieval decision for the full user message."""
    decision: str
    exact_items: List[RetrievalItem]
    candidates_by_slot: Dict[int, List[RetrievalItem]]
    diagnostics: Dict[str, Any] | None = None


# ------------------------------
# Contracts (adapters implement these)
# ------------------------------

class TextEncoder(Protocol):
    """Embed a text into a dense vector."""
    def embed(self, text: str) -> List[float]: ...


class LexicalStore(Protocol):
    """BM25/FTS-like backend."""
    def upsert(self, doc: IndexedDoc) -> Result[None, AppError]: ...
    def upsert_many(self, docs: Iterable[IndexedDoc]) -> Result[None, AppError]: ...
    def search(self, query: str, k: int, filters: Optional[Dict[str, Any]] = None) -> Result[List[Tuple[str, float]], AppError]: ...
    def remove(self, doc_id: str) -> Result[None, AppError]: ...


class VectorStore(Protocol):
    """ANN/VectorDB-like backend."""
    def upsert(self, doc: IndexedDoc) -> Result[None, AppError]: ...
    def upsert_many(self, docs: Iterable[IndexedDoc]) -> Result[None, AppError]: ...
    def query(self, vector: List[float], k: int, filters: Optional[Dict[str, Any]] = None) -> Result[List[Tuple[str, float]], AppError]: ...
    def remove(self, doc_id: str) -> Result[None, AppError]: ...


class DocSerializer(Protocol):
    """Convert arbitrary source record -> IndexedDoc."""
    def to_indexed_doc(self, record: Dict[str, Any]) -> Result[IndexedDoc, AppError]: ...


class SlotParser(Protocol):
    """Split message into slots and extract soft hints."""
    def parse(self, user_message: str) -> List[QuerySlot]: ...


# ------------------------------
# Configuration
# ------------------------------

@dataclass(frozen=True)
class IndexerConfig:
    compute_vectors: bool = True


@dataclass(frozen=True)
class RetrieverConfig:
    k_lexical: int = 50
    k_vector: int = 50
    k_final: int = 5
    tau_exact: float = 0.90
    delta_margin: float = 0.10
    tau_some: float = 0.50


# ------------------------------
# Utilities (scoring and fusion)
# ------------------------------

def _minmax_norm(values: List[float]) -> List[float]:
    if not values:
        return values
    lo, hi = min(values), max(values)
    if math.isclose(lo, hi):
        return [0.5] * len(values)
    span = (hi - lo)
    return [(v - lo) / span for v in values]


def _fuse_lexical_vector(
    lex_hits: List[Tuple[str, float]],
    vec_hits: List[Tuple[str, float]],
    alpha: float = 0.5,
) -> List[Tuple[str, float]]:
    """Normalize scores and combine with weighted sum; deduplicate by best score."""
    lex_ids, lex_scores = zip(*lex_hits) if lex_hits else ([], [])
    vec_ids, vec_scores = zip(*vec_hits) if vec_hits else ([], [])
    lex_norm = _minmax_norm(list(lex_scores)) if lex_hits else []
    vec_norm = _minmax_norm(list(vec_scores)) if vec_hits else []

    fused: Dict[str, float] = {}
    for i, did in enumerate(lex_ids):
        fused[did] = max(fused.get(did, 0.0), alpha * lex_norm[i])
    for i, did in enumerate(vec_ids):
        fused[did] = fused.get(did, 0.0) + (1 - alpha) * vec_norm[i]

    return sorted(fused.items(), key=lambda x: x[1], reverse=True)


# ------------------------------
# Default simple SlotParser
# ------------------------------

class BasicSlotParser:
    """
    Conservative splitter on ',', ' y ', ' and '.
    Keeps hints empty; adapters can subclass and add NER/regex hints.
    """
    _seps = [",", " y ", " and "]

    def parse(self, user_message: str) -> List[QuerySlot]:
        text = (user_message or "").strip().lower()
        if not text:
            return []
        parts: List[str] = [text]
        for sep in self._seps:
            tmp: List[str] = []
            for p in parts:
                tmp.extend([x.strip() for x in p.split(sep) if x.strip()])
            parts = tmp
        return [QuerySlot(text=p, hints={}) for p in parts]


# ------------------------------
# Indexer
# ------------------------------

class Indexer:
    """
    Serialize records, compute vectors (optional), and upsert into stores.
    Uses Result/AppError for adapter errors and LogBus for observability.
    """

    def __init__(
        self,
        serializer: DocSerializer,
        lexical: LexicalStore,
        vector: Optional[VectorStore],
        encoder: Optional[TextEncoder],
        config: IndexerConfig = IndexerConfig(),
        log_topic: str = "rag.indexer",
    ) -> None:
        self._ser = serializer
        self._lex = lexical
        self._vec = vector
        self._enc = encoder
        self._cfg = config
        self._log = LogBus.instance().topic(log_topic)

    def upsert_many(self, records: Iterable[Dict[str, Any]]) -> Result[None, AppError]:
        batch: List[IndexedDoc] = []
        for r in records:
            ser_res = self._ser.to_indexed_doc(r)
            if ser_res.is_err():
                err = ser_res.unwrap_err()
                self._log.error(lambda: f"serializer failed doc={r.get('id')}", exc=err)
                return Result.Err(err)
            doc = ser_res.unwrap()

            if self._cfg.compute_vectors:
                if self._enc is None:
                    err = AppError.bad_request("Vector computation enabled but encoder is None")
                    self._log.error("encoder missing for vector computation", exc=err)
                    return Result.Err(err)
                vec = self._enc.embed(doc.text_index)
                doc = IndexedDoc(doc_id=doc.doc_id, text_index=doc.text_index, metadata=doc.metadata, vector=vec)

            batch.append(doc)

        # Upsert lexical
        res_lex = self._lex.upsert_many(batch)
        if res_lex.is_err():
            err = res_lex.unwrap_err()
            self._log.error("lexical upsert_many failed", exc=err)
            return Result.Err(err)

        # Upsert vectors if applicable
        if self._cfg.compute_vectors and self._vec is not None:
            only_vec = [d for d in batch if d.vector is not None]
            res_vec = self._vec.upsert_many(only_vec)
            if res_vec.is_err():
                err = res_vec.unwrap_err()
                self._log.error("vector upsert_many failed", exc=err)
                return Result.Err(err)

        self._log.debug(lambda: f"indexed docs={len(batch)}")
        return Result.Ok(None)

    def upsert_one(self, record: Dict[str, Any]) -> Result[None, AppError]:
        return self.upsert_many([record])

    def remove(self, doc_id: str) -> Result[None, AppError]:
        res1 = self._lex.remove(doc_id)
        if res1.is_err():
            err = res1.unwrap_err()
            self._log.error(lambda: f"lexical remove failed doc_id={doc_id}", exc=err)
            return Result.Err(err)
        if self._vec is not None:
            res2 = self._vec.remove(doc_id)
            if res2.is_err():
                err = res2.unwrap_err()
                self._log.error(lambda: f"vector remove failed doc_id={doc_id}", exc=err)
                return Result.Err(err)
        self._log.debug(lambda: f"removed doc_id={doc_id}")
        return Result.Ok(None)


# ------------------------------
# Retriever
# ------------------------------

class Retriever:
    """
    Hybrid retrieval with decision policy (EXACT/CANDIDATES/NONE).
    Errors from adapters are surfaced via Result.
    """

    def __init__(
        self,
        lexical: LexicalStore,
        vector: Optional[VectorStore],
        encoder: Optional[TextEncoder],
        slot_parser: Optional[SlotParser] = None,
        config: RetrieverConfig = RetrieverConfig(),
        log_topic: str = "rag.retriever",
    ) -> None:
        self._lex = lexical
        self._vec = vector
        self._enc = encoder
        self._parser = slot_parser or BasicSlotParser()
        self._cfg = config
        self._log = LogBus.instance().topic(log_topic)

    def retrieve(self, user_message: str) -> Result[RetrievalResult, AppError]:
        slots = self._parser.parse(user_message)
        if not slots:
            rr = RetrievalResult(
                decision=RetrievalDecision.NONE,
                exact_items=[],
                candidates_by_slot={},
                diagnostics={"reason": "empty_query"},
            )
            return Result.Ok(rr)

        exact_items: List[RetrievalItem] = []
        candidates_by_slot: Dict[int, List[RetrievalItem]] = {}
        any_ambiguous = False
        any_none = False
        per_slot_diags: Dict[int, Any] = {}

        for i, slot in enumerate(slots):
            # Lexical candidates
            sr = self._lex.search(slot.text, k=self._cfg.k_lexical, filters=None)
            if sr.is_err():
                err = sr.unwrap_err()
                self._log.error(lambda: f"lexical search failed slot={i} q={slot.text!r}", exc=err)
                return Result.Err(err)
            lex_hits = sr.unwrap()

            # Vector candidates
            vec_hits: List[Tuple[str, float]] = []
            if self._vec is not None and self._enc is not None:
                qvec = self._enc.embed(slot.text)
                vr = self._vec.query(qvec, k=self._cfg.k_vector, filters=None)
                if vr.is_err():
                    err = vr.unwrap_err()
                    self._log.error(lambda: f"vector query failed slot={i}", exc=err)
                    return Result.Err(err)
                vec_hits = vr.unwrap()

            fused = _fuse_lexical_vector(lex_hits, vec_hits, alpha=0.5)[: max(self._cfg.k_final, 1)]
            raw_scores = [s for _, s in fused]
            norm_scores = _minmax_norm(raw_scores)
            items = [
                RetrievalItem(doc_id=doc_id, score=norm_scores[idx], metadata={})
                for idx, (doc_id, _s) in enumerate(fused)
            ]

            if not items:
                any_none = True
                candidates_by_slot[i] = []
                per_slot_diags[i] = {"decision": "NONE", "reason": "no_candidates"}
                continue

            top1 = items[0]
            top2 = items[1] if len(items) > 1 else None
            margin = top1.score - (top2.score if top2 else 0.0)

            if top1.score >= self._cfg.tau_exact and margin >= self._cfg.delta_margin:
                exact_items.append(top1)
                per_slot_diags[i] = {"decision": "EXACT", "top1": (top1.doc_id, top1.score), "margin": margin}
            elif top1.score >= self._cfg.tau_some:
                any_ambiguous = True
                candidates_by_slot[i] = items
                per_slot_diags[i] = {
                    "decision": "CANDIDATES",
                    "candidates": [(it.doc_id, it.score) for it in items],
                }
            else:
                any_none = True
                candidates_by_slot[i] = []
                per_slot_diags[i] = {"decision": "NONE", "top1": (top1.doc_id, top1.score)}

        if exact_items and not any_ambiguous and not any_none:
            decision = RetrievalDecision.EXACT
        elif any_ambiguous:
            decision = RetrievalDecision.CANDIDATES
        elif any_none and not exact_items:
            decision = RetrievalDecision.NONE
        else:
            decision = RetrievalDecision.CANDIDATES  # mixed case

        res = RetrievalResult(
            decision=decision,
            exact_items=exact_items,
            candidates_by_slot=candidates_by_slot,
            diagnostics={"slots": [s.text for s in slots], "per_slot": per_slot_diags, "config": self._cfg.__dict__},
        )
        self._log.debug(lambda: f"retrieve decision={decision} slots={len(slots)}")
        return Result.Ok(res)
