# tests/test_rag_pipeline.py
from __future__ import annotations
import os
import re
import uuid
import psycopg
import pytest

from convo_orchestrator.adapters.encoder_ollama import OllamaEncoder
from convo_orchestrator.adapters.postgres_lexical import PostgresLexicalStore
from convo_orchestrator.adapters.qdrant_store import QdrantVectorStore

PG_TABLE = "rag_docs_e2e"
Q_COLL = "rag_e2e_coll"


def _dsn() -> str:
    """Build a DSN from environment variables with sensible defaults."""
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "55432")
    user = os.getenv("PGUSER", "postgres")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "postgres")
    return f"host={host} port={port} user={user} password={pwd} dbname={db}"


def _norm(s: str | None) -> str:
    """Lowercase, trim, and collapse repeated whitespace."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _tok(s: str | None) -> list[str]:
    """Whitespace tokenization after normalization."""
    return _norm(s).split()


def _parse_requested_terms(user_msg: str) -> list[str]:
    """
    Split a user request into independent product-like terms.

    Notes:
        - Splits on Spanish "y", English "and", and commas.
        - Removes common Spanish stop-words found in short product requests.
    """
    parts = re.split(r"\s+y\s+|,|\s+and\s+", user_msg, flags=re.IGNORECASE)
    stop = r"\b(quiero|la|el|los|las|un|una|de|del|para|por|favor|me|gustaria|quiero)\b"
    cleaned = []
    for r in parts:
        r = re.sub(stop, " ", r, flags=re.IGNORECASE)
        r = _norm(r).replace("(", " ").replace(")", " ")
        if r:
            cleaned.append(r)
    return cleaned


def _extract_size_tokens(text: str) -> set[str]:
    """Extract size tokens like '5ml', '100ml' from text."""
    toks = set()
    for m in re.finditer(r"\b(\d{1,4})\s*ml\b", _norm(text)):
        toks.add(f"{m.group(1)}ml")
    return toks


def _token_groups(term: str) -> list[set[str]]:
    """
    Tokenize a term into groups; tokens containing '/' are treated as OR groups.
    Example: 'sunscreen/bronzer' -> [{'sunscreen', 'bronzer'}]
    """
    groups: list[set[str]] = []
    for t in _tok(term):
        if "/" in t:
            alts = {a for a in re.split(r"/+", t) if a}
            groups.append(alts)
        else:
            groups.append({t})
    return groups


@pytest.mark.integration
def test_rag_pipeline_exact_options_none():
    # ----- Infrastructure -----
    model = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")
    enc = OllamaEncoder(model=model, endpoint=f"http://localhost:{os.getenv('OLLAMA_PORT','11434')}/api/embeddings")

    # Fresh table
    with psycopg.connect(_dsn(), autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {PG_TABLE} CASCADE;")

    # Backends
    lex = PostgresLexicalStore(dsn=_dsn(), table=PG_TABLE, ts_config="simple")
    assert lex.ensure_schema().is_ok()

    dim = len(enc.embed("dimension probe e2e"))
    vs = QdrantVectorStore(
        collection=Q_COLL,
        host="localhost",
        port=int(os.getenv("QDRANT_PORT", "6333")),
        vector_size=dim,
        distance="Cosine",
        on_missing_create=True,
    )
    assert vs.ensure_collection().is_ok()

    # ----- Dataset -----
    ids = [str(uuid.UUID(int=i)) for i in range(1, 9)]
    P1, P2, P3, P4, P5, P6, P7, P8 = ids

    products = [
        (P1, "Nivea Creme Moisturizing Cream (Azul / Blue Tin) 100ml – classic formula",
         {"id": P1, "name": "Nivea Creme (Azul) 100ml",
          "brand": "Nivea", "size": "100ml",
          "description": "Crema hidratante clásica en lata azul para todo tipo de piel."}),
        (P2, "Carolina Herrera Sun Bronzer SPF15 5ml – Travel Kit / Kit de viaje",
         {"id": P2, "name": "Carolina Herrera Sun Bronzer SPF15 5ml Travel Kit",
          "brand": "Carolina Herrera", "size": "5ml",
          "description": "Mini bronzer SPF15, ideal para viaje; formato kit."}),
        (P3, "Nivea Creme Soft 75ml (White Edition)",
         {"id": P3, "name": "Nivea Creme Soft 75ml White Edition"}),
        (P4, "Nivea Body Lotion Aloe Vera 400ml hydrating",
         {"id": P4, "name": "Nivea Body Lotion Aloe Vera 400ml"}),
        (P5, "Sunscreen Lotion by Carolina Herrera 30ml (white tube)",
         {"id": P5, "name": "Carolina Herrera Sunscreen 30ml"}),
        (P6, "Dove Repair Shampoo 250ml – reparación profunda",
         {"id": P6, "name": "Shampoo Dove reparación 250ml"}),
        (P7, "Nivea Creme Classic 100 ml White Tin (Blanco)",
         {"id": P7, "name": "Nivea Creme Classic 100ml (Blanco)"}),
        (P8, "Kit Crema hidratante universal 100ml (no brand)",
         {"id": P8, "name": "Universal Moisturizing Cream Kit 100ml", "description": "sin marca"}),
    ]

    # Index in Postgres + Qdrant
    pg_rows = [(pid, title + (". " + meta["description"] if meta.get("description") else ""), meta)
               for pid, title, meta in products]
    assert lex.upsert_many(pg_rows).is_ok()

    vec_items = [(pid, enc.embed(title + (". " + meta.get("description", ""))), meta)
                 for pid, title, meta in products]
    assert vs.upsert_many(vec_items).is_ok()

    # ----------- Pipeline -----------
    user_msg = "Quiero la crema Nivea azul y el bronzer de Carolina Herrera travel de 5ml"
    requested = _parse_requested_terms(user_msg)
    assert requested

    decided, suggestions = {}, {}

    for term in requested:
        term_groups = _token_groups(term)
        term_sizes = _extract_size_tokens(term)
        flat_toks = set().union(*term_groups)

        lres = lex.search(term, limit=8).unwrap()
        vres = vs.search(enc.embed(term), limit=8).unwrap()

        scores = {}

        def add(hits, w: float):
            for h in hits:
                scores[h.doc_id] = scores.get(h.doc_id, 0.0) + w * float(h.score or 0.0)

        add(lres, 1.7)
        add(vres, 1.0)

        meta_by_id = {h.doc_id: h.metadata for h in lres}
        meta_by_id.update({h.doc_id: h.metadata for h in vres})

        # --- Simple fusion scoring ---
        for doc_id, sc in list(scores.items()):
            meta = meta_by_id.get(doc_id, {}) or {}
            text = _norm(meta.get("name", "") + " " + meta.get("description", ""))
            toks = set(_tok(text))
            # +0.4 for exact size token
            for sz in term_sizes:
                if sz in text:
                    sc += 0.4
            # +0.2 per covered group token
            sc += 0.2 * sum(1 for grp in term_groups if grp & toks)
            scores[doc_id] = sc

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:6]

        def covers(doc_id: str) -> bool:
            text = _norm((meta_by_id.get(doc_id) or {}).get("name", "") + " " +
                         (meta_by_id.get(doc_id) or {}).get("description", ""))
            toks = set(_tok(text))
            # All OR-groups must have at least one token present
            return all(grp & toks for grp in term_groups if grp)

        if top and covers(top[0][0]):
            decided[term] = top[0][0]
        else:
            sug = [{"doc_id": d, "score": s, "name": (meta_by_id.get(d) or {}).get("name")}
                   for d, s in top[:3]]
            suggestions[term] = sug

    if len(decided) == len(requested):
        outcome, context = "exact", list(decided.values())
    elif any(suggestions.values()):
        outcome, context = "options", suggestions
    else:
        outcome, context = "none", None

    # For this dataset we expect EXACT: P1 (Nivea) and P2 (CH kit)
    assert outcome == "exact", f"expected 'exact', got {outcome} with context={context}"
    assert set(context) == {P1, P2}


@pytest.mark.integration
def test_rag_pipeline_options_when_ambiguous():
    """
    Expect 'options' when the top candidate does not fully cover the requested tokens.
    Example query: "nivea crema 100ml kit" — P1 has 100ml but not "kit"; P8 has "kit" but not "nivea".
    """
    # Lightweight re-setup (keeps same Qdrant collection and PG table)
    model = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")
    enc = OllamaEncoder(model=model, endpoint=f"http://localhost:{os.getenv('OLLAMA_PORT','11434')}/api/embeddings")

    user_msg = "Quiero la Nivea crema 100ml kit"
    requested = _parse_requested_terms(user_msg)
    assert requested

    def run(term: str):
        """Inline pipeline executor returning (outcome, context) for a single term."""
        term_groups = _token_groups(term)
        term_sizes = _extract_size_tokens(term)
        flat_toks = set().union(*term_groups)

        lres = lex.search(term, limit=8).unwrap()
        vres = vs.search(enc.embed(term), limit=8).unwrap()

        scores = {}

        def add(hits, w: float):
            for h in hits:
                scores[h.doc_id] = scores.get(h.doc_id, 0.0) + w * float(h.score or 0.0)

        add(lres, 1.7)
        add(vres, 1.0)

        meta_by_id = {h.doc_id: h.metadata for h in lres}
        meta_by_id.update({h.doc_id: h.metadata for h in vres})

        for doc_id, sc in list(scores.items()):
            meta = meta_by_id.get(doc_id, {}) or {}
            text = _norm(meta.get("name", "") + " " + meta.get("description", ""))
            toks = set(_tok(text))
            for sz in term_sizes:
                if sz in text:
                    sc += 0.4
            sc += 0.2 * sum(1 for grp in term_groups if grp & toks)
            scores[doc_id] = sc

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:6]

        def covers(doc_id: str) -> bool:
            text = _norm((meta_by_id.get(doc_id) or {}).get("name", "") + " " +
                         (meta_by_id.get(doc_id) or {}).get("description", ""))
            toks = set(_tok(text))
            return all(grp & toks for grp in term_groups if grp) and all(sz in text for sz in term_sizes)

        if top and covers(top[0][0]):
            return "exact", [top[0][0]]

        # fallback: 'options'
        sug = [{"doc_id": d, "score": s, "name": (meta_by_id.get(d) or {}).get("name")}
               for d, s in top[:3]]
        return "options", {term: sug}

    # Re-create lightweight handles if needed
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "55432")
    user = os.getenv("PGUSER", "postgres")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "postgres")
    dsn = f"host={host} port={port} user={user} password={pwd} dbname={db}"

    lex = PostgresLexicalStore(dsn=dsn, table=PG_TABLE, ts_config="simple")
    dim = len(enc.embed("probe for options"))
    vs = QdrantVectorStore(collection=Q_COLL, host="localhost", port=int(os.getenv("QDRANT_PORT", "6333")), vector_size=dim)

    outcome, context = run(requested[0])
    assert outcome == "options", f"expected 'options', got {outcome} with {context}"
    # should include at least two reasonable suggestions
    assert isinstance(context, dict) and len(next(iter(context.values()))) >= 2


@pytest.mark.integration
def test_rag_pipeline_none_with_low_overlap_filter():
    """
    Expect 'none' when no candidate meets a minimum token-overlap threshold.
    Vector stores always return neighbors, so we apply an explicit overlap filter.
    """
    MIN_OVERLAP = 0.5  # at least 50% of term tokens must be present to consider a suggestion

    model = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")
    enc = OllamaEncoder(model=model, endpoint=f"http://localhost:{os.getenv('OLLAMA_PORT','11434')}/api/embeddings")

    user_msg = "Necesito lorex ultra purple 9999ml quantum foam"
    requested = _parse_requested_terms(user_msg)
    assert requested

    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "55432")
    user = os.getenv("PGUSER", "postgres")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "postgres")
    dsn = f"host={host} port={port} user={user} password={pwd} dbname={db}"

    lex = PostgresLexicalStore(dsn=dsn, table=PG_TABLE, ts_config="simple")
    dim = len(enc.embed("probe for none"))
    vs = QdrantVectorStore(collection=Q_COLL, host="localhost", port=int(os.getenv("QDRANT_PORT", "6333")), vector_size=dim)

    decided = {}
    suggestions = {}

    for term in requested:
        term_groups = _token_groups(term)
        term_sizes = _extract_size_tokens(term)
        term_tokens = set().union(*term_groups)

        lres = lex.search(term, limit=8).unwrap()
        vres = vs.search(enc.embed(term), limit=8).unwrap()

        scores = {}

        def add(hits, w: float):
            for h in hits:
                scores[h.doc_id] = scores.get(h.doc_id, 0.0) + w * float(h.score or 0.0)

        add(lres, 1.7)
        add(vres, 1.0)

        meta_by_id = {h.doc_id: h.metadata for h in lres}
        meta_by_id.update({h.doc_id: h.metadata for h in vres})

        # Re-rank and filter by minimum token overlap
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:6]

        def token_overlap_ratio(doc_id: str) -> float:
            meta = meta_by_id.get(doc_id, {}) or {}
            text = _norm(meta.get("name", "") + " " + meta.get("description", ""))
            toks = set(_tok(text))
            if not term_tokens:
                return 0.0
            return len(term_tokens & toks) / len(term_tokens)

        filtered = [(d, s) for d, s in ranked if token_overlap_ratio(d) >= MIN_OVERLAP]

        if filtered:
            def covers(doc_id: str) -> bool:
                meta = meta_by_id.get(doc_id, {}) or {}
                text = _norm(meta.get("name", "") + " " + meta.get("description", ""))
                toks = set(_tok(text))
                if not all(grp & toks for grp in term_groups if grp):
                    return False
                return all(sz in text for sz in term_sizes)

            if covers(filtered[0][0]):
                decided[term] = filtered[0][0]
            else:
                suggestions[term] = [{"doc_id": d, "score": s, "name": (meta_by_id.get(d) or {}).get("name")}
                                     for d, s in filtered[:3]]

    # Outcome resolution
    if not decided and not any(suggestions.values()):
        outcome, context = "none", None
    elif decided:
        outcome, context = "exact", list(decided.values())
    else:
        outcome, context = "options", suggestions

    assert outcome == "none", f"expected 'none', got {outcome} with context={context}"
