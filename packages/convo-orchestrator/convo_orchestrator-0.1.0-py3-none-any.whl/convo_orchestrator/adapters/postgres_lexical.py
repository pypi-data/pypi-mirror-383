# adapters/postgres_lexical.py
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

import psycopg
from psycopg.types.json import Json

from ..shared import Result, AppError, LogBus, ErrorKind
from ..domain.rag_domain import LexicalStore, RetrievalItem


class PostgresLexicalStore(LexicalStore):
    """
    PostgreSQL-backed lexical store using `tsvector` + GIN.

    Features:
        - Schema bootstrap with a generated tsvector column and GIN index.
        - Upsert documents with JSONB metadata.
        - Ranked text search using `plainto_tsquery` and `ts_rank`.

    Safety:
        - `ts_config` is validated against a conservative regex before being inlined in DDL.
          (The DDL for generated columns cannot use parameters.)
    """

    # Example valid configs: simple, english, spanish, etc.
    _TSCONF_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    def __init__(
        self,
        dsn: str,
        table: str = "rag_docs",
        ts_config: str = "simple",
        log_topic: str = "rag.pg",
    ) -> None:
        self._dsn = dsn
        self._table = table
        self._ts_config = ts_config
        self._log = LogBus.instance().topic(log_topic)
        self._ensure_once = False

    def _conn(self) -> psycopg.Connection:
        """Create a new connection with autocommit enabled."""
        return psycopg.connect(self._dsn, autocommit=True)

    # --- Schema ----------------------------------------------------------------

    def ensure_schema(self) -> Result[None, AppError]:
        """
        Ensure the documents table and GIN index exist.

        Returns:
            Ok(None) if the schema is present/created; Err(AppError) on failure.
        """
        if self._ensure_once:
            return Result.Ok(None)

        # Validate ts_config to avoid SQL injection when inlining into DDL
        if not self._TSCONF_RE.match(self._ts_config):
            return Result.Err(AppError(ErrorKind.BAD_REQUEST, f"invalid ts_config: {self._ts_config!r}"))

        # Generated column DDL must inline the regconfig; cannot parameterize.
        ts_expr = f"to_tsvector('{self._ts_config}'::regconfig, coalesce(text,''))"

        try:
            with self._conn() as conn, conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table} (
                        doc_id TEXT PRIMARY KEY,
                        text   TEXT NOT NULL,
                        meta   JSONB NOT NULL DEFAULT '{{}}',
                        tsv    tsvector GENERATED ALWAYS AS (
                                  {ts_expr}
                                ) STORED
                    );
                    """
                )
                cur.execute(
                    f"CREATE INDEX IF NOT EXISTS {self._table}_gin ON {self._table} USING GIN(tsv);"
                )

            self._ensure_once = True
            self._log.debug(lambda: f"pg schema ensured table={self._table}")
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"ensure_schema: {ex}"))

    # --- Mutation --------------------------------------------------------------

    def upsert_many(self, items: Iterable[Tuple[str, str, Dict[str, Any]]]) -> Result[None, AppError]:
        """
        Insert or update multiple documents.

        Args:
            items: Iterable of (doc_id, text, metadata).

        Returns:
            Ok(None) on success; Err(AppError) on failure.
        """
        try:
            with self._conn() as conn, conn.cursor() as cur:
                for doc_id, text, meta in items:
                    cur.execute(
                        f"""
                        INSERT INTO {self._table}(doc_id, text, meta)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (doc_id) DO UPDATE
                        SET text = EXCLUDED.text, meta = EXCLUDED.meta
                        """,
                        (doc_id, text or "", Json(meta or {})),
                    )
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"upsert_many: {ex}"))

    def remove(self, doc_id: str) -> Result[None, AppError]:
        """
        Delete a document by its ID.

        Args:
            doc_id: Document identifier.

        Returns:
            Ok(None) on success; Err(AppError) on failure.
        """
        try:
            with self._conn() as conn, conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self._table} WHERE doc_id=%s", (doc_id,))
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"remove: {ex}"))

    # --- Query -----------------------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Result[List[RetrievalItem], AppError]:
        """
        Full-text search using `plainto_tsquery` and rank by `ts_rank`.

        Args:
            query: Raw query string.
            limit: Maximum number of results.
            filters: Optional JSONB containment filter applied to `meta`.

        Returns:
            Ok(list of RetrievalItem) on success; Err(AppError) on failure.
        """
        try:
            with self._conn() as conn, conn.cursor() as cur:
                sql = f"""
                    WITH q AS (SELECT plainto_tsquery(%s::regconfig, %s) AS tsq)
                    SELECT d.doc_id, d.meta, ts_rank(d.tsv, q.tsq) AS score
                    FROM {self._table} d, q
                    WHERE d.tsv @@ q.tsq
                """
                params: List[Any] = [self._ts_config, query]

                if filters:
                    sql += " AND d.meta @> %s::jsonb"
                    params.append(Json(filters))

                sql += " ORDER BY score DESC LIMIT %s"
                params.append(limit)

                cur.execute(sql, params)
                rows = cur.fetchall()

            items = [
                RetrievalItem(
                    doc_id=r[0],
                    score=float(r[2] or 0.0),
                    metadata=dict(r[1] or {}),
                )
                for r in rows
            ]
            return Result.Ok(items)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"search: {ex}"))
