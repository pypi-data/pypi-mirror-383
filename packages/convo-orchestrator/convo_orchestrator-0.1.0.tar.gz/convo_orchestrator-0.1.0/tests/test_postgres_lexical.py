# tests/test_postgres_lexical.py
from __future__ import annotations

import os
import psycopg
import pytest

from convo_orchestrator.adapters.postgres_lexical import PostgresLexicalStore


def _dsn() -> str:
    """Build a DSN from environment variables with sensible defaults."""
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "55432")
    user = os.getenv("PGUSER", "postgres")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "postgres")
    return f"host={host} port={port} user={user} password={pwd} dbname={db}"


@pytest.mark.integration
def test_pg_lexical_upsert_and_search():
    store = PostgresLexicalStore(dsn=_dsn(), table="rag_docs_test", ts_config="simple")

    # Idempotent cleanup
    with psycopg.connect(_dsn(), autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS rag_docs_test CASCADE;")

    assert store.ensure_schema().is_ok()

    docs = [
        ("p1", "Crema Nivea hidratante 100ml", {"name": "Crema Nivea", "brand": "Nivea"}),
        ("p2", "Bronceador Carolina Herrera 5ml SPF15", {"name": "Bronceador Carolina Herrera 5ml", "brand": "Carolina Herrera"}),
        ("p3", "Shampoo Dove reparación", {"name": "Shampoo Dove", "brand": "Dove"}),
    ]
    assert store.upsert_many(docs).is_ok()

    # Basic lexical search
    hits = store.search("crema nivea", limit=5)
    assert hits.is_ok(), f"search failed: {hits}"
    items = hits.unwrap()
    assert items, "expected at least one lexical hit"
    assert items[0].metadata.get("name", "").lower().startswith("crema nivea")

    # Search with metadata filter
    hits_f = store.search("carolina", limit=5, filters={"brand": "Carolina Herrera"})
    assert hits_f.is_ok()
    items_f = hits_f.unwrap()
    assert items_f and all(it.metadata.get("brand") == "Carolina Herrera" for it in items_f)

    # Filter that should return no results
    hits_none = store.search("carolina", limit=5, filters={"brand": "Nivea"})
    assert hits_none.is_ok()
    assert hits_none.unwrap() == []
