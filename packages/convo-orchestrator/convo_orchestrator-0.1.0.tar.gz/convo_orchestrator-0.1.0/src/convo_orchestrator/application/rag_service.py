# application/rag_service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..shared import Result, AppError, LogBus
from ..domain.rag_domain import (
    Indexer,
    Retriever,
    RetrievalResult,
    RetrievalDecision,
    RetrievalItem,
)


# ---------------------------
# DTOs for LLM-facing context
# ---------------------------

@dataclass(frozen=True)
class LLMExactItem:
    """Slim view of an exact match sent to the LLM."""
    doc_id: str
    score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class LLMCandidates:
    """Slim view of top-N candidates for one slot."""
    slot_idx: int
    items: List[LLMExactItem]


@dataclass(frozen=True)
class LLMContext:
    """
    Single payload handed to the LLM as context:
    - mode='exact'        -> items contains the authoritative docs.
    - mode='candidates'   -> candidates_by_slot contains plausible options.
    - mode='none'         -> nothing found with confidence.
    """
    mode: str
    items: List[LLMExactItem]
    candidates_by_slot: List[LLMCandidates]
    diagnostics: Optional[Dict[str, Any]] = None


# ---------------------------
# Mapping helpers
# ---------------------------

def _to_llm_item(it: RetrievalItem) -> LLMExactItem:
    return LLMExactItem(doc_id=it.doc_id, score=float(it.score), metadata=dict(it.metadata or {}))


def _result_to_llm_ctx(rr: RetrievalResult) -> LLMContext:
    if rr.decision == RetrievalDecision.EXACT:
        return LLMContext(
            mode="exact",
            items=[_to_llm_item(it) for it in rr.exact_items],
            candidates_by_slot=[],
            diagnostics=rr.diagnostics or {},
        )
    if rr.decision == RetrievalDecision.CANDIDATES:
        cand = [
            LLMCandidates(
                slot_idx=i,
                items=[_to_llm_item(it) for it in (rr.candidates_by_slot.get(i) or [])],
            )
            for i in sorted(rr.candidates_by_slot.keys())
        ]
        return LLMContext(
            mode="candidates",
            items=[],
            candidates_by_slot=cand,
            diagnostics=rr.diagnostics or {},
        )
    # NONE
    return LLMContext(mode="none", items=[], candidates_by_slot=[], diagnostics=rr.diagnostics or {})


# ---------------------------
# Application service façade
# ---------------------------

class RagService:
    """
    Thin façade to expose high-level use cases:
      - index(records): serialize -> (lexical, vector) upserts
      - remove(doc_id): delete from both indices
      - retrieve_to_llm(message): hybrid search -> LLMContext (exact/candidates/none)

    Errors are surfaced as Result.Err(AppError) without raising.
    Logging uses the shared LogBus with a dedicated topic.
    """

    def __init__(self, indexer: Indexer, retriever: Retriever, log_topic: str = "rag.app") -> None:
        self._indexer = indexer
        self._retriever = retriever
        self._log = LogBus.instance().topic(log_topic)

    # ---- Use cases -------------------------------------------------

    def index(self, records: List[Dict[str, Any]]) -> Result[None, AppError]:
        if not records:
            return Result.Ok(None)
        res = self._indexer.upsert_many(records)
        if res.is_err():
            err = res.unwrap_err()
            self._log.error("index failed", exc=err)
            return Result.Err(err)
        self._log.debug(lambda: f"indexed count={len(records)}")
        return Result.Ok(None)

    def remove(self, doc_id: str) -> Result[None, AppError]:
        if not doc_id:
            return Result.Err(AppError.bad_request("doc_id is empty"))
        res = self._indexer.remove(doc_id)
        if res.is_err():
            err = res.unwrap_err()
            self._log.error(lambda: f"remove failed doc_id={doc_id}", exc=err)
            return Result.Err(err)
        self._log.debug(lambda: f"removed doc_id={doc_id}")
        return Result.Ok(None)

    def retrieve_to_llm(self, user_message: str) -> Result[LLMContext, AppError]:
        if not user_message or not user_message.strip():
            ctx = LLMContext(mode="none", items=[], candidates_by_slot=[], diagnostics={"reason": "empty_query"})
            return Result.Ok(ctx)

        rr_res = self._retriever.retrieve(user_message)
        if rr_res.is_err():
            err = rr_res.unwrap_err()
            self._log.error("retrieve failed", exc=err, extra={"q": user_message[:128]})
            return Result.Err(err)

        rr = rr_res.unwrap()
        ctx = _result_to_llm_ctx(rr)
        self._log.debug(lambda: f"retrieve ok mode={ctx.mode} items={len(ctx.items)} slots={len(ctx.candidates_by_slot)}")
        return Result.Ok(ctx)
