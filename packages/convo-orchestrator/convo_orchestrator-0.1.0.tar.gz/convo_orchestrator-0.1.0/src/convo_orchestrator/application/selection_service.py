# application/selection_service.py

from __future__ import annotations

from typing import Any, Dict, List, Set

from ..domain.selection import (
    LexicalStore,
    VectorStore,
    TextEncoder,
    SelectionOptions,
    SelectionResult,
    SearchOutcome,
)


"""
Heuristic selection service that decides among EXACT / OPTIONS / NONE outcomes.

The service queries both lexical and vector stores, merges scores per document,
and then applies simple coverage and attribute checks (colors, sizes) to decide
whether the query maps to a single exact item, to a short list of options, or to
no suitable result.
"""

# Simple bilingual color tokens (heuristic only; used when require_attrs=True).
COLOR_TOKS: Set[str] = {
    "blue", "white", "black", "red", "green",
    "azul", "blanco", "negro", "rojo", "verde",
}


def _norm(s: str) -> str:
    """
    Normalize a string by lowercasing and collapsing whitespace.

    Args:
        s: Input string.

    Returns:
        Normalized string.
    """
    return " ".join((s or "").lower().split())


def _tok(s: str) -> List[str]:
    """
    Tokenize a string using whitespace after normalization.

    Args:
        s: Input string.

    Returns:
        List of tokens.
    """
    return _norm(s).split()


def _extract_size_tokens(query: str) -> Set[str]:
    """
    Extract size-like tokens from the query (e.g., '100ml', '250g', '1l', '2oz').

    Args:
        query: Raw query text.

    Returns:
        Set of tokens that look like sizes or quantities.
    """
    toks = _tok(query)
    out: Set[str] = set()
    for t in toks:
        if any(t.endswith(u) for u in ["ml", "l", "g", "kg", "oz"]):
            out.add(t)
    return out


def decide_exact_options_none(
    query: str,
    *,
    lex_store: LexicalStore,
    vec_store: VectorStore,
    encoder: TextEncoder,
    opts: SelectionOptions = SelectionOptions(),
) -> SelectionResult:
    """
    Decide whether the query matches an EXACT item, a list of OPTIONS, or NONE.

    Strategy:
        1) Retrieve lexical and vector candidates.
        2) Merge scores across sources per doc_id, applying weights from options.
        3) Compute token coverage and (optionally) attribute constraints.
        4) Return:
            - EXACT if the best candidate meets full coverage and attribute checks.
            - OPTIONS if enough candidates pass minimum coverage, limited by top_k_options.
            - NONE otherwise.

    Args:
        query: Raw user query.
        lex_store: Lexical search backend.
        vec_store: Vector similarity backend.
        encoder: Text encoder used to embed the query for vector search.
        opts: SelectionOptions controlling weights and thresholds.

    Returns:
        SelectionResult describing the chosen outcome and its payload.
    """
    # 1) Candidate retrieval
    limit = max(8, opts.top_k_options)
    lhits = lex_store.search(query, limit=limit).unwrap_or([])
    qvec = encoder.embed(query)
    vhits = vec_store.search(qvec, limit=limit).unwrap_or([])

    # 2) Score fusion by doc_id
    scores: Dict[str, float] = {}
    meta_by_id: Dict[str, Dict[str, Any]] = {}

    def add(hits: List[Any], w: float) -> None:
        for h in hits or []:
            scores[h.doc_id] = scores.get(h.doc_id, 0.0) + w * float(getattr(h, "score", 0.0) or 0.0)
            if h.doc_id not in meta_by_id:
                meta_by_id[h.doc_id] = dict(getattr(h, "metadata", {}) or {})

    add(lhits, opts.lex_weight)
    add(vhits, opts.vec_weight)

    if not scores:
        return SelectionResult(SearchOutcome.NONE, None)

    # 3) Query signals
    q_tokens: Set[str] = set(_tok(query)) - {"/"}  # ignore slash separators
    req_colors: Set[str] = q_tokens & COLOR_TOKS
    req_sizes: Set[str] = _extract_size_tokens(query)

    def text_of(doc_id: str) -> str:
        m = meta_by_id.get(doc_id) or {}
        return _norm((m.get("name") or "") + " " + (m.get("description") or ""))

    def cover_ratio(doc_id: str) -> float:
        if not q_tokens:
            return 0.0
        t = set(_tok(text_of(doc_id)))
        hit = sum(1 for x in q_tokens if x in t)
        return hit / max(1, len(q_tokens))

    def attrs_match(doc_id: str) -> bool:
        """
        Attribute gate used when `require_attrs` is enabled in options.

        - Sizes: accepts candidates where any word contains each requested size token.
        - Colors: requires that all requested color tokens appear as full tokens.
        """
        if not opts.require_attrs:
            return True
        tset = set(_tok(text_of(doc_id)))
        sz_ok = all(any(sz in w for w in tset) for sz in req_sizes) if req_sizes else True
        col_ok = req_colors.issubset(tset) if req_colors else True
        return sz_ok and col_ok

    # 4) Preliminary ranking
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    # 5) EXACT
    if ranked:
        best_id, _ = ranked[0]
        if cover_ratio(best_id) >= opts.exact_cover and attrs_match(best_id):
            return SelectionResult(SearchOutcome.EXACT, best_id)

    # 6) OPTIONS (respect top_k_options)
    options: List[Dict[str, Any]] = []
    for doc_id, sc in ranked:
        if cover_ratio(doc_id) >= opts.options_min_cover:
            m = meta_by_id.get(doc_id) or {}
            options.append({"doc_id": doc_id, "name": m.get("name"), "score": sc})
        if len(options) >= opts.top_k_options:
            break

    if options:
        return SelectionResult(SearchOutcome.OPTIONS, options)

    # 7) NONE
    return SelectionResult(SearchOutcome.NONE, None)
