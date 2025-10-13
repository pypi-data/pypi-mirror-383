# examples/sales_assistand.py
from __future__ import annotations
import asyncio
import hashlib
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple
from urllib import request as urlreq

import psycopg
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ===================== Configuration =====================
PG_DSN = os.getenv(
    "CHAT_PG_DSN",
    "host=localhost port=55432 user=postgres password=postgres dbname=postgres",
)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")
GEN_MODEL = os.getenv("RAG_GEN_MODEL", "llama3:latest")

# Summarization / context window
CTX_WINDOW_CHARS = int(os.getenv("CTX_WINDOW_CHARS", "1500"))
CTX_MARGIN_CHARS = int(os.getenv("CTX_MARGIN_CHARS", "150"))

# Retrieval
TOPK_OPTIONS = int(os.getenv("TOPK_OPTIONS", "5"))
Q_COLL = os.getenv("RAG_Q_COLLECTION", "rag_example_products")
PG_TABLE = os.getenv("RAG_PG_TABLE", "rag_docs_example")

# ===================== RAG adapters =====================
from convo_orchestrator.adapters.postgres_lexical import PostgresLexicalStore
from convo_orchestrator.adapters.qdrant_store import QdrantVectorStore
from convo_orchestrator.adapters.encoder_ollama import OllamaEncoder
from convo_orchestrator.application.selection_service import (
    decide_exact_options_none,
    SelectionOptions,
)
from convo_orchestrator import (
    InMemoryEventRepository,
    InMemoryMetrics,
    SystemClock,
    EventManager,
    HandlerRegistry,
    Event,
    EventId,
    Policy,
)

# ===================== Utilities =====================
def _norm(s: str | None) -> str:
    """Lowercase, trim, and collapse whitespace."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _tok(s: str | None) -> list[str]:
    """Tokenize after normalization."""
    return _norm(s).split()


def _extract_size_tokens(text: str) -> set[str]:
    """Extract size mentions like '100ml' as normalized tokens."""
    toks: set[str] = set()
    for m in re.finditer(r"\b(\d{1,4})\s*ml\b", _norm(text or "")):
        toks.add(f"{m.group(1)}ml")
    return toks


def _token_groups(term: str) -> list[set[str]]:
    """
    Token groups with '/' are treated as OR groups.
    Example: 'white/soft cream' -> [{'white'}, {'soft'}, {'cream'}]; 'spf/bronzer' -> [{'spf','bronzer'}]
    """
    groups: list[set[str]] = []
    for t in _tok(term):
        if "/" in t:
            alts = {a for a in re.split(r"/+", t) if a}
            groups.append(alts)
        else:
            groups.append({t})
    return groups


def _join_msgs(msgs: List[Dict[str, Any]]) -> str:
    """Join chat messages as plain text."""
    return " \n".join(f"{m['role']}: {m['content']}" for m in msgs)


# ===================== INTENT & RESPONSE Prompts =====================
INTENT_PROMPT = """\
<|begin_of_system|>
You are a classifier for a cosmetics customer–sales chat.

Your task:
1) Decide if the conversation shows a LIVE COMMERCIAL INTENT and is NOT closed.
2) If YES, extract each referenced product mention as a short string including all observed detail
   (codes, sizes in ml, descriptors like "soft white cream", etc.). Do not hallucinate.

Output:
- If NO → empty JSON: {}
- If YES → {"products": ["<mention 1>", "<mention 2>", ...]}

Rules:
- STRICT, VALID JSON only (no extra text).
- Use concise English.

SUMMARY:
{summary_block}

HISTORY (excluding the latest customer message):
{history_block}

CUSTOMER MESSAGE:
{latest_user}
<|end_of_system|>
"""

RESPONSE_PROMPT = """\
<|begin_of_system|>
You are an assistant in a cosmetics customer–sales conversation.
Guide the customer to create or modify an order (code + quantity) using the context.

Context:
- SUMMARY
- HISTORY (recent messages, excluding the latest customer message)
- FOUND PRODUCTS (valid options)
- CUSTOMER MESSAGE

Rules:
1) Use the context. If ambiguous, ask briefly; do not invent.
2) Do not provide prices or past order details.
3) You may gently say that "a sales rep will contact you shortly" if appropriate.
4) Return STRICT JSON only:
   {{
     "response": "<text>",                         // ALWAYS non-empty string.
     "current_order": [{{"product_id":"ID","quantity":<int>}}] | null,
     "confirmed": true | false
   }}
5) In "response", when you mention products, use EXACTLY: "(<id>) <full name>".
6) Do NOT add products without 100% identification (from FOUND PRODUCTS).
7) If the customer changes quantities or products, update the order accordingly.
8) If FOUND PRODUCTS is "(empty)", do not assert availability; either ask a short identification question
   OR say a sales rep will follow up (choose one).

FOUND PRODUCTS:
{context_block}

HISTORY:
{history_block}

SUMMARY:
{summary_block}

MESSAGE:
Customer: {latest_user}
<|end_of_system|>
"""

# ===================== LLM wrapper (Ollama /api/generate) =====================
class OllamaLLM:
    """Thin wrapper around Ollama's /api/generate endpoint."""

    def __init__(self, model: str, endpoint: Optional[str] = None):
        self.model = model
        self.endpoint = endpoint or f"http://localhost:{OLLAMA_PORT}/api/generate"

    def _call(self, payload: Dict[str, Any]) -> str:
        body = json.dumps(payload).encode("utf-8")
        req = urlreq.Request(
            self.endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urlreq.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return (data.get("response") or "").strip()

    def complete_json(self, prompt: str, temperature: float = 0.0) -> str:
        return self._call(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": temperature},
            }
        )

    def complete_text(self, prompt: str, temperature: float = 0.2) -> str:
        return self._call(
            {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        )


# ===================== Infra (DB) =====================
def pg_conn():
    """Open a psycopg connection with autocommit."""
    return psycopg.connect(PG_DSN, autocommit=True)


def ensure_tables():
    """Create the minimal schema for chats/messages, idempotency, RAG corpus, products, and summaries."""
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS chats(
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          metadata JSONB,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );"""
        )
        cur.execute("CREATE INDEX IF NOT EXISTS chats_created ON chats(created_at DESC);")

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS messages(
          id TEXT PRIMARY KEY,
          chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
          role TEXT NOT NULL CHECK (role IN ('user','server')),
          content TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          meta JSONB
        );"""
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS messages_chat_time ON messages(chat_id, created_at DESC);"
        )

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS idempotency_keys(
          key TEXT PRIMARY KEY,
          body_sha256 TEXT NOT NULL,
          response JSONB NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );"""
        )

        # RAG corpus
        cur.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {PG_TABLE} (
            doc_id TEXT PRIMARY KEY,
            text   TEXT NOT NULL,
            meta   JSONB NOT NULL DEFAULT '{{}}',
            tsv    tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text,''))) STORED
        );"""
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS {PG_TABLE}_gin ON {PG_TABLE} USING GIN(tsv);"
        )

        # Products catalog
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            brand TEXT,
            size TEXT,
            lang TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );"""
        )
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS products_name_trgm ON products USING GIN (name gin_trgm_ops);"
            )
        except Exception:
            cur.execute(
                "CREATE INDEX IF NOT EXISTS products_name_lower_idx ON products (LOWER(name));"
            )

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS chat_summaries (
            id BIGSERIAL PRIMARY KEY,
            chat_id TEXT NOT NULL,
            upto_msg_id TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            ts TIMESTAMPTZ NOT NULL DEFAULT now()
        );"""
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS chat_summaries_idx ON chat_summaries(chat_id, ts DESC);"
        )


# ===================== RAG setup =====================
encoder = OllamaEncoder(model=EMBED_MODEL, endpoint=f"http://localhost:{OLLAMA_PORT}/api/embeddings")
lex = PostgresLexicalStore(dsn=PG_DSN, table=PG_TABLE, ts_config="simple")
_probe_dim = len(encoder.embed("probe"))
vec = QdrantVectorStore(collection=Q_COLL, host=QDRANT_HOST, port=QDRANT_PORT, vector_size=_probe_dim)
lex.ensure_schema()
vec.ensure_collection()


def reindex_products_into_rag(rows: List[Dict[str, Any]]) -> None:
    """Index/refresh the given products in Postgres (lexical) and Qdrant (vector)."""
    if not rows:
        return
    pg_items, vec_items = [], []
    for r in rows:
        pid = r["id"]
        name = (r.get("name") or "").strip()
        desc = (r.get("description") or "").strip()
        text = name if not desc else f"{name}. {desc}"
        meta = {"id": pid, "name": name, "description": desc}
        pg_items.append((pid, text, meta))
        vec_items.append((pid, encoder.embed(text), meta))
    assert lex.upsert_many(pg_items).is_ok()
    assert vec.upsert_many(vec_items).is_ok()


def upsert_products_pg(rows: List[Dict[str, Any]]) -> None:
    """Upsert products into the catalog table."""
    if not rows:
        return
    with pg_conn() as conn, conn.cursor() as cur:
        for r in rows:
            cur.execute(
                """INSERT INTO products (id,name,description,brand,size,lang)
                           VALUES (%s,%s,%s,%s,%s,%s)
                           ON CONFLICT (id) DO UPDATE
                           SET name=EXCLUDED.name,description=EXCLUDED.description,
                               brand=EXCLUDED.brand,size=EXCLUDED.size,lang=EXCLUDED.lang
            """,
                (
                    r.get("id"),
                    r.get("name"),
                    r.get("description"),
                    r.get("brand"),
                    r.get("size"),
                    r.get("lang"),
                ),
            )


def upsert_products_and_index(rows: List[Dict[str, Any]]) -> None:
    """Upsert products and index them in both stores."""
    upsert_products_pg(rows)
    reindex_products_into_rag(rows)


def _seed_demo_products() -> list[dict]:
    """Minimal demo catalog to make the example usable out of the box."""
    return [
        {
            "id": "NV100BLUE",
            "name": "Nivea Cream Blue Tin 100 ml",
            "description": "Classic moisturizing cream in a blue tin.",
            "brand": "Nivea",
            "size": "100ml",
            "lang": "en",
        },
        {
            "id": "NVSFT75WT",
            "name": "Nivea Cream Soft White Edition 75 ml",
            "description": "Soft version with white lid.",
            "brand": "Nivea",
            "size": "75ml",
            "lang": "en",
        },
        {
            "id": "NVALOE400",
            "name": "Nivea Body Lotion Aloe Vera 400 ml",
            "description": "Body lotion with aloe vera.",
            "brand": "Nivea",
            "size": "400ml",
            "lang": "en",
        },
        {
            "id": "NV100WHT",
            "name": "Nivea Cream White Tin 100 ml",
            "description": "Cream in white tin.",
            "brand": "Nivea",
            "size": "100ml",
            "lang": "en",
        },
        {
            "id": "NVBABY200",
            "name": "Nivea Baby Soft Cream 200 ml",
            "description": "Gentle cream for babies.",
            "brand": "Nivea",
            "size": "200ml",
            "lang": "en",
        },
    ]


# ===================== Schemas =====================
class Chat(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    metadata: Optional[Dict[str, Any]] = None


class CreateChatRequest(BaseModel):
    title: str
    metadata: Optional[Dict[str, Any]] = None


class CreateChatResponse(BaseModel):
    chat: Chat


class UpdateChatRequest(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class UpdateChatResponse(BaseModel):
    chat: Chat


class ChatsListResponse(BaseModel):
    chats: List[Chat]
    next_cursor: Optional[str] = None


class Message(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    created_at: str
    meta: Optional[Dict[str, Any]] = None


class MessagePostRequest(BaseModel):
    chat_id: str
    content: str
    meta: Optional[Dict[str, Any]] = None


class MessagePostResponse(BaseModel):
    status: str
    message: Message


class MessagesListResponse(BaseModel):
    messages: List[Message]
    next_cursor: Optional[str] = None


# ===================== Services (OO) =====================
class ChatService:
    """CRUD for chat records."""

    def create(self, title: str, metadata: Optional[Dict[str, Any]]) -> Chat:
        chat_id = f"ch_{uuid.uuid4().hex[:8]}"
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO chats(id,title,metadata) VALUES(%s,%s,%s)
                           RETURNING id,title,metadata,created_at,updated_at""",
                (chat_id, title, json.dumps(metadata) if metadata is not None else None),
            )
            r = cur.fetchone()
        return Chat(
            id=r[0],
            title=r[1],
            metadata=r[2],
            created_at=r[3].isoformat() + "Z",
            updated_at=r[4].isoformat() + "Z",
        )

    def list(self, limit: int = 50, cursor: Optional[str] = None) -> ChatsListResponse:
        with pg_conn() as conn, conn.cursor() as cur:
            if cursor:
                cur.execute(
                    """SELECT id,title,metadata,created_at,updated_at
                               FROM chats WHERE created_at < %s ORDER BY created_at DESC LIMIT %s""",
                    (cursor, limit),
                )
            else:
                cur.execute(
                    """SELECT id,title,metadata,created_at,updated_at
                               FROM chats ORDER BY created_at DESC LIMIT %s""",
                    (limit,),
                )
            rows = cur.fetchall()
        chats = [
            Chat(
                id=r[0],
                title=r[1],
                metadata=r[2],
                created_at=r[3].isoformat() + "Z",
                updated_at=r[4].isoformat() + "Z",
            )
            for r in rows
        ]
        next_cursor = rows[-1][3].isoformat() + "Z" if rows and len(rows) == limit else None
        return ChatsListResponse(chats=chats, next_cursor=next_cursor)

    def update(self, chat_id: str, title: Optional[str], metadata: Optional[Dict[str, Any]]) -> Chat:
        if not title and metadata is None:
            raise HTTPException(
                400,
                detail={
                    "error": {
                        "code": "INVALID_ARGUMENT",
                        "message": "At least one of title or metadata",
                    }
                },
            )
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}})
            if title is not None and metadata is not None:
                cur.execute(
                    """UPDATE chats SET title=%s, metadata=%s, updated_at=now()
                               WHERE id=%s RETURNING id,title,metadata,created_at,updated_at""",
                    (title, json.dumps(metadata), chat_id),
                )
            elif title is not None:
                cur.execute(
                    """UPDATE chats SET title=%s, updated_at=now()
                               WHERE id=%s RETURNING id,title,metadata,created_at,updated_at""",
                    (title, chat_id),
                )
            else:
                cur.execute(
                    """UPDATE chats SET metadata=%s, updated_at=now()
                               WHERE id=%s RETURNING id,title,metadata,created_at,updated_at""",
                    (json.dumps(metadata) if metadata is not None else None, chat_id),
                )
            r = cur.fetchone()
        return Chat(
            id=r[0],
            title=r[1],
            metadata=r[2],
            created_at=r[3].isoformat() + "Z",
            updated_at=r[4].isoformat() + "Z",
        )

    def delete(self, chat_id: str) -> None:
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM chats WHERE id=%s", (chat_id,))
            if cur.rowcount == 0:
                raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}})


class MessageService:
    """Message persistence for user/server messages."""

    def create_user_message(self, chat_id: str, content: str, meta: Optional[Dict[str, Any]]) -> Message:
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}})
            mid = f"msg_usr_{uuid.uuid4().hex[:8]}"
            cur.execute(
                """INSERT INTO messages(id,chat_id,role,content,meta)
                           VALUES(%s,%s,'user',%s,%s)
                           RETURNING id,chat_id,role,content,created_at,meta""",
                (mid, chat_id, content, json.dumps(meta) if meta is not None else None),
            )
            r = cur.fetchone()
        return Message(
            id=r[0], chat_id=r[1], role=r[2], content=r[3], created_at=r[4].isoformat() + "Z", meta=r[5]
        )

    def create_server_message(self, chat_id: str, content: str, meta: Optional[Dict[str, Any]]) -> Message:
        with pg_conn() as conn, conn.cursor() as cur:
            mid = f"msg_srv_{uuid.uuid4().hex[:8]}"
            cur.execute(
                """INSERT INTO messages(id,chat_id,role,content,meta)
                           VALUES(%s,%s,'server',%s,%s)
                           RETURNING id,chat_id,role,content,created_at,meta""",
                (mid, chat_id, content, json.dumps(meta) if meta is not None else None),
            )
            r = cur.fetchone()
        return Message(
            id=r[0], chat_id=r[1], role=r[2], content=r[3], created_at=r[4].isoformat() + "Z", meta=r[5]
        )

    def list(self, chat_id: str, limit: int = 50, before: Optional[str] = None) -> MessagesListResponse:
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}})
            if before:
                cur.execute(
                    """SELECT id,chat_id,role,content,created_at,meta
                               FROM messages
                               WHERE chat_id=%s AND id < %s
                               ORDER BY created_at DESC
                               LIMIT %s""",
                    (chat_id, before, limit),
                )
            else:
                cur.execute(
                    """SELECT id,chat_id,role,content,created_at,meta
                               FROM messages
                               WHERE chat_id=%s
                               ORDER BY created_at DESC
                               LIMIT %s""",
                    (chat_id, limit),
                )
            rows = cur.fetchall()
        msgs = [
            Message(
                id=r[0], chat_id=r[1], role=r[2], content=r[3], created_at=r[4].isoformat() + "Z", meta=r[5]
            )
            for r in rows
        ]
        next_cursor = rows[-1][0] if rows and len(rows) == limit else None
        return MessagesListResponse(messages=msgs, next_cursor=next_cursor)


# ===================== Orchestrator (OO) =====================
class RAGOrchestrator:
    """Intent detection → retrieval/selection → response planning → SSE."""

    def __init__(self):
        self.llm = OllamaLLM(model=GEN_MODEL)

    def get_latest_summary(self, chat_id: str) -> Tuple[str, Optional[str]]:
        """Return (summary_text, upto_msg_id) for the chat if present."""
        try:
            with pg_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT summary_text, upto_msg_id
                               FROM chat_summaries
                               WHERE chat_id=%s
                               ORDER BY ts DESC
                               LIMIT 1""",
                    (chat_id,),
                )
                row = cur.fetchone()
                if row:
                    return (row[0] or ""), row[1]
        except Exception:
            pass
        return "", None

    def list_messages_all(self, chat_id: str, exclude_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Chronological list of messages; optionally exclude one id."""
        with pg_conn() as conn, conn.cursor() as cur:
            if exclude_id:
                cur.execute(
                    """SELECT id, role, content, created_at
                               FROM messages
                               WHERE chat_id=%s AND id <> %s
                               ORDER BY created_at ASC""",
                    (chat_id, exclude_id),
                )
            else:
                cur.execute(
                    """SELECT id, role, content, created_at
                               FROM messages
                               WHERE chat_id=%s
                               ORDER BY created_at ASC""",
                    (chat_id,),
                )
            rows = cur.fetchall()
        return [{"id": r[0], "role": r[1], "content": r[2], "ts": r[3].isoformat() + "Z"} for r in rows]

    def maybe_summarize(self, chat_id: str) -> None:
        """Summarize the conversation if context grows beyond the window (+margin)."""
        msgs = self.list_messages_all(chat_id)
        if not msgs:
            return
        prev_summary, _prev_upto = self.get_latest_summary(chat_id)
        text_all = (prev_summary + "\n" + _join_msgs(msgs)).strip()
        if len(text_all) <= CTX_WINDOW_CHARS + CTX_MARGIN_CHARS:
            return
        upto_id = msgs[-1]["id"]
        prompt = f"""\
<|begin_of_system|>
Summarize (in English) the customer–sales–assistant conversation for a cosmetics ordering bot.
Include only essentials to proceed (products, quantities, confirmations, open questions).
Maximum {CTX_WINDOW_CHARS} characters. Plain text.
<|end_of_system|>

PREVIOUS SUMMARY:
{prev_summary or "(empty)"}

HISTORY TO SUMMARIZE:
{_join_msgs(msgs)}
"""
        short = self.llm.complete_text(prompt, temperature=0.0).strip()
        if not short:
            return
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO chat_summaries(chat_id,upto_msg_id,summary_text,ts)
                           VALUES(%s,%s,%s,now())""",
                (chat_id, upto_id, short),
            )

    def _collect_history(
        self, chat_id: str, exclude_id: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Tuple[str, Optional[str]]]:
        """Prefer messages after the last summary; otherwise use last few."""
        all_msgs = self.list_messages_all(chat_id, exclude_id)
        summary_text, upto = self.get_latest_summary(chat_id)
        if upto:
            after = [m for m in all_msgs if m["id"] > upto]
            if len(after) >= 3:
                hist = after
            else:
                hist = all_msgs[-3:] if len(all_msgs) >= 3 else (after or all_msgs)
        else:
            hist = all_msgs
        return hist, (summary_text, upto)

    def build_intent_prompt(self, chat_id: str, latest_user_text: str, latest_user_id: Optional[str]) -> str:
        """Prompt for product-mention intent detection."""
        history, (summary_text, upto) = self._collect_history(chat_id, exclude_id=latest_user_id)
        history_block = "\n".join([f"{m['role']}: {m['content']}" for m in history]) if history else "(empty)"
        return INTENT_PROMPT.format(
            summary_block=summary_text or "(empty)",
            history_block=history_block,
            latest_user=latest_user_text,
        )

    def parse_intent_json(self, raw: str) -> Dict[str, Any]:
        """Parse classifier JSON output; return {} or {'products': [...]}."""
        try:
            data = json.loads(raw) if raw else {}
            if isinstance(data, dict):
                if "products" in data:
                    prods = data.get("products")
                    if isinstance(prods, list):
                        return {"products": [str(x).strip() for x in prods if str(x).strip()]}
                    return {"products": []}
                return {}
        except Exception as ex:
            print("[intent.parse.error]", ex, raw[:200])
        return {}

    def find_products_for_terms(self, terms: List[str], topk_per_term: int = TOPK_OPTIONS) -> List[Dict[str, str]]:
        """
        For each term, use decide_exact_options_none + lightweight fusion to gather allowed products.
        Returns unique [{'id': product_id, 'name': product_name}, ...]
        """
        if not terms:
            return []
        dedup: Dict[str, str] = {}

        for original in terms:
            term = _norm(original)
            if not term:
                continue

            sel = decide_exact_options_none(
                term,
                lex_store=lex,
                vec_store=vec,
                encoder=encoder,
                opts=SelectionOptions(top_k_options=topk_per_term, exact_cover=1.0, options_min_cover=0.0),
            )

            if sel.outcome.value == "exact":
                did = sel.context
                if did:
                    with pg_conn() as conn, conn.cursor() as cur:
                        cur.execute("SELECT name FROM products WHERE id=%s LIMIT 1", (did,))
                        row = cur.fetchone()
                    dedup[did] = (row[0] if row else did)
            elif sel.outcome.value == "options":
                for it in (sel.context or []):
                    did = it.get("doc_id")
                    nm = it.get("name") or did
                    if did:
                        dedup.setdefault(did, nm)

            # Extra fusion step for robustness
            try:
                lres = lex.search(term, limit=max(topk_per_term, 8)).unwrap()
                vres = vec.search(encoder.embed(term), limit=max(topk_per_term, 8)).unwrap()
            except Exception as ex:
                print("[search.warn]", ex)
                lres, vres = [], []

            scores: Dict[str, float] = {}

            def add(hits, w: float):
                for h in hits:
                    scores[h.doc_id] = scores.get(h.doc_id, 0.0) + w * float(h.score or 0.0)

            add(lres, 1.7)
            add(vres, 1.0)

            meta_by_id: Dict[str, Dict[str, Any]] = {h.doc_id: (h.metadata or {}) for h in lres}
            meta_by_id.update({h.doc_id: (h.metadata or {}) for h in vres})

            term_groups = _token_groups(term)
            term_sizes = _extract_size_tokens(term)

            def text_of(doc_id: str) -> str:
                meta = meta_by_id.get(doc_id, {}) or {}
                return _norm((meta.get("name") or "") + " " + (meta.get("description") or ""))

            for doc_id, sc in list(scores.items()):
                txt = text_of(doc_id)
                toks = set(_tok(txt))
                for sz in term_sizes:
                    if sz in txt:
                        sc += 0.4
                sc += 0.2 * sum(1 for grp in term_groups if grp & toks)
                scores[doc_id] = sc

            ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

            def covers(doc_id: str) -> bool:
                toks = set(_tok(text_of(doc_id)))
                return all(grp & toks for grp in term_groups if grp)

            covering = [doc_id for doc_id, _ in ranked if covers(doc_id)]
            picked = covering[:topk_per_term] if covering else [doc_id for doc_id, _ in ranked[: min(3, topk_per_term)]]
            for doc_id in picked:
                nm = (meta_by_id.get(doc_id) or {}).get("name") or doc_id
                dedup.setdefault(doc_id, nm)

        return [{"id": k, "name": v} for k, v in dedup.items()]

    def build_response_prompt(
        self,
        chat_id: str,
        latest_user_text: str,
        latest_user_id: Optional[str],
        allowed_products: List[Dict[str, str]],
    ) -> str:
        """Build planning prompt constrained to the allowed products."""
        history, (summary_text, _) = self._collect_history(chat_id, exclude_id=latest_user_id)
        context_block = "\n".join([f"- ({p['id']}) {p['name']}" for p in allowed_products]) if allowed_products else "(empty)"
        history_block = "\n".join([f"{m['role']}: {m['content']}" for m in history]) if history else "(empty)"
        return RESPONSE_PROMPT.format(
            context_block=context_block,
            history_block=history_block,
            summary_block=summary_text or "(empty)",
            latest_user=latest_user_text,
        )

    def _safe_parse_llm_json(self, raw: str) -> Dict[str, Any]:
        """Parse JSON; try to recover if extra text surrounds the object."""
        base = {"response": "", "current_order": None, "confirmed": False}
        if not raw:
            return base
        try:
            data = json.loads(raw)
        except Exception:
            try:
                start = raw.index("{")
                end = raw.rindex("}") + 1
                data = json.loads(raw[start:end])
            except Exception as ex:
                print("[_safe_parse_llm_json] parse error:", ex, "raw:", raw[:200])
                return base
        out = {
            "response": (data.get("response") or "").strip(),
            "current_order": data.get("current_order"),
            "confirmed": bool(data.get("confirmed", False)),
        }
        if isinstance(out["current_order"], list) and not out["current_order"]:
            out["current_order"] = None
        return out

    def sanitize_llm_output(self, data: Dict[str, Any], allowed_products: List[Dict[str, str]]) -> Dict[str, Any]:
        """Enforce that current_order only contains allowed product ids and valid quantities."""
        allowed_ids = {p["id"] for p in allowed_products}
        data["confirmed"] = bool(data.get("confirmed", False))
        resp = data.get("response")
        data["response"] = (resp if isinstance(resp, str) else "").strip()

        valid_items: List[Dict[str, Any]] = []
        order = data.get("current_order")
        if isinstance(order, list):
            for it in order:
                if not isinstance(it, dict):
                    continue
                pid = it.get("product_id")
                qty = it.get("quantity")
                if isinstance(pid, str) and pid in allowed_ids and isinstance(qty, int) and qty > 0:
                    valid_items.append({"product_id": pid, "quantity": qty})
        data["current_order"] = valid_items if valid_items else None

        if not allowed_products:
            data["current_order"] = None
        return data

    async def process_user_message(self, msg: Message, sse_notifier: "SSEHub"):
        """End-to-end pipeline for an incoming user message."""
        chat_id = msg.chat_id
        try:
            self.maybe_summarize(chat_id)
        except Exception as ex:
            print("[summarize.warn]", ex)

        intent_prompt = self.build_intent_prompt(chat_id, msg.content, latest_user_id=msg.id)
        intent_raw = self.llm.complete_json(intent_prompt, temperature=0.0)
        intent = self.parse_intent_json(intent_raw)
        print("[intent.raw]", intent_raw)

        if isinstance(intent, dict) and not intent:
            await sse_notifier.emit(chat_id, {"event": "status", "data": {"state": "skipped"}})
            return

        terms = intent.get("products", []) if isinstance(intent, dict) else []
        allowed_products = self.find_products_for_terms(terms, topk_per_term=TOPK_OPTIONS)

        resp_prompt = self.build_response_prompt(
            chat_id, msg.content, latest_user_id=msg.id, allowed_products=allowed_products
        )
        print("[llm.resp_prompt]", resp_prompt)
        raw = self.llm.complete_json(resp_prompt, temperature=0.0)
        data = self.sanitize_llm_output(self._safe_parse_llm_json(raw), allowed_products)
        print("[llm.raw]", raw)

        text = data.get("response", "").strip()
        meta = {"model": GEN_MODEL, "allowed_products": allowed_products, "confirmed": data.get("confirmed")}
        if text:
            await sse_notifier.emit(chat_id, {"event": "status", "data": {"state": "started"}})
            for i in range(0, len(text), 25):
                await sse_notifier.emit(chat_id, {"event": "token", "data": {"chunk": text[i : i + 25]}})
                await asyncio.sleep(0.01)
            srv_msg = MessageService().create_server_message(chat_id, text, meta)
            await sse_notifier.emit(chat_id, {"event": "message", "data": srv_msg.dict()})
            await sse_notifier.emit(chat_id, {"event": "status", "data": {"state": "completed"}})
        else:
            await sse_notifier.emit(chat_id, {"event": "status", "data": {"state": "empty"}})


# ===================== SSE Hub =====================
class SSEHub:
    """In-memory SSE hub keyed by chat_id."""

    def __init__(self):
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    async def subscribe(self, chat_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self._listeners.setdefault(chat_id, []).append(q)
        return q

    def unsubscribe(self, chat_id: str, q: asyncio.Queue):
        if chat_id in self._listeners:
            self._listeners[chat_id] = [qq for qq in self._listeners[chat_id] if qq is not q]
            if not self._listeners[chat_id]:
                del self._listeners[chat_id]

    async def emit(self, chat_id: str, payload: Dict[str, Any]):
        for q in list(self._listeners.get(chat_id, [])):
            await q.put(payload)

    async def stream(self, chat_id: str):
        """Async generator that yields SSE-formatted chunks."""
        q = await self.subscribe(chat_id)
        try:
            # initial heartbeat so clients hook the stream immediately
            yield b": ping\n\n"
            while True:
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=10.0)
                    ev = payload.get("event", "message")
                    data = payload.get("data", {})
                    ev_id = f"ev_{uuid.uuid4().hex[:6]}"
                    # Always format as SSE (event, id, data)
                    yield f"event: {ev}\n".encode()
                    yield f"id: {ev_id}\n".encode()
                    yield ("data: " + json.dumps(data, ensure_ascii=False) + "\n\n").encode()
                except asyncio.TimeoutError:
                    # periodic heartbeat; prevents proxies from buffering/closing
                    yield b": ping\n\n"
        finally:
            self.unsubscribe(chat_id, q)


# ===================== Idempotency =====================
class Idempotency:
    """Simple idempotency helper based on a caller-provided key."""

    @staticmethod
    def _hash_body(obj: Any) -> str:
        return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    @staticmethod
    def check_and_store(key: str, body: Dict[str, Any], response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        h = Idempotency._hash_body(body)
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT body_sha256, response FROM idempotency_keys WHERE key=%s", (key,))
            row = cur.fetchone()
            if row:
                if row[0] != h:
                    raise HTTPException(
                        409,
                        detail={
                            "error": {
                                "code": "IDEMPOTENCY_CONFLICT",
                                "message": "Different body for same Idempotency-Key",
                            }
                        },
                    )
                return row[1]
            cur.execute(
                "INSERT INTO idempotency_keys(key, body_sha256, response) VALUES(%s,%s,%s)",
                (key, h, json.dumps(response)),
            )
        return None


# ===================== Event manager wiring =====================
_event_repo = InMemoryEventRepository()
_event_metrics = InMemoryMetrics()
_event_clock = SystemClock()
_handler_registry = HandlerRegistry()
event_mgr = EventManager(
    repo=_event_repo,
    handler_registry=_handler_registry,
    clock=_event_clock,
    metrics=_event_metrics,
    scheduler_tick_ms=200,  # adequate for simple intervals
)

REPLY_EVENT_ID = EventId("ev-chat-reply")


# Handler that runs the pipeline and emits over SSE
async def _handle_reply(ctx):
    payload = ctx.payload or {}
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    print(f"[handler chat-reply] start chat={chat_id} msg={message_id}")

    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT id, chat_id, role, content, created_at, meta
                       FROM messages WHERE id=%s LIMIT 1""",
            (message_id,),
        )
        row = cur.fetchone()
    if not row:
        print(f"[handler chat-reply] message not found: {message_id}")
        return "skip (message not found)"

    msg = Message(
        id=row[0], chat_id=row[1], role=row[2], content=row[3], created_at=row[4].isoformat() + "Z", meta=row[5]
    )

    await orchestrator.process_user_message(msg, sse_hub)
    print(f"[handler chat-reply] done chat={chat_id} msg={message_id}")
    return "ok"


# Register handler
_handler_registry.register("chat-reply", _handle_reply)

# Create (or idempotent) event record
_reply_event = Event(
    id=REPLY_EVENT_ID,
    name="chat-reply",
    handler_name="chat-reply",  # refers to the handler's registered name
    policy=Policy(timeout_sec=90.0, max_retries=0, max_concurrency=1),
    active=True,
)
_event_repo.save_event(_reply_event)

# ===================== App & Routes =====================
app = FastAPI(title="User↔Server Chat API", version="1.0.0", description="REST + SSE API for multi-chat")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

chat_svc = ChatService()
msg_svc = MessageService()
orchestrator = RAGOrchestrator()
sse_hub = SSEHub()


@app.on_event("startup")
def _startup():
    ensure_tables()
    try:
        upsert_products_and_index(_seed_demo_products())
        print("[startup] Seeded + indexed demo products")
    except Exception as ex:
        print("[startup] seed/index failed:", ex)

    print("[startup] starting EventManager")
    event_mgr.start()


@app.on_event("shutdown")
async def _shutdown():
    print("[shutdown] stopping EventManager")
    await event_mgr.stop()


# ---- /v1/chats ----
@app.get("/v1/chats", response_model=ChatsListResponse)
def list_chats(limit: int = 50, cursor: Optional[str] = None):
    return chat_svc.list(limit=limit, cursor=cursor)


@app.post("/v1/chats", status_code=201, response_model=CreateChatResponse)
def create_chat(body: CreateChatRequest):
    chat = chat_svc.create(body.title, body.metadata)
    return CreateChatResponse(chat=chat)


@app.patch("/v1/chats/{chat_id}", response_model=UpdateChatResponse)
def update_chat(chat_id: str, body: UpdateChatRequest):
    chat = chat_svc.update(chat_id, body.title, body.metadata)
    return UpdateChatResponse(chat=chat)


@app.delete("/v1/chats/{chat_id}", status_code=204)
def delete_chat(chat_id: str):
    chat_svc.delete(chat_id)
    return Response(status_code=204)


# ---- /v1/chats/{chat_id}/messages ----
@app.get("/v1/chats/{chat_id}/messages", response_model=MessagesListResponse)
def list_messages(chat_id: str, limit: int = 50, before: Optional[str] = None):
    return msg_svc.list(chat_id=chat_id, limit=limit, before=before)


# ---- /v1/messages (idempotent publish) ----
@app.post("/v1/messages", status_code=202, response_model=MessagePostResponse)
async def publish_message(
    body: MessagePostRequest, Idempotency_Key: Optional[str] = Header(default=None, convert_underscores=False)
):
    msg = msg_svc.create_user_message(body.chat_id, body.content, body.meta)
    resp = {"status": "queued", "message": msg.dict()}

    if Idempotency_Key:
        prev = Idempotency.check_and_store(Idempotency_Key, body.dict(), resp)
        if prev:
            return JSONResponse(prev, status_code=202)

    # Notify SSE clients that the work is queued
    asyncio.create_task(sse_hub.emit(msg.chat_id, {"event": "status", "data": {"state": "queued"}}))

    async def _emit_later():
        try:
            print(f"[emit_later] will emit in 60s for chat={msg.chat_id} msg={msg.id}")
            await asyncio.sleep(60.0)
            res = await event_mgr.emit(REPLY_EVENT_ID, payload={"chat_id": msg.chat_id, "message_id": msg.id})
            if res.is_ok():
                print(f"[emit_later] emitted job → {REPLY_EVENT_ID.value}")
            else:
                print(f"[emit_later] emit failed: {res}")
                await sse_hub.emit(msg.chat_id, {"event": "status", "data": {"state": "error", "detail": "emit failed"}})
        except Exception as ex:
            print("[emit_later.error]", ex)
            await sse_hub.emit(msg.chat_id, {"event": "status", "data": {"state": "error", "detail": str(ex)}})

    asyncio.create_task(_emit_later())
    return MessagePostResponse(**resp)


# ---- SSE ----
@app.get("/v1/chats/{chat_id}/stream")
async def stream_chat(chat_id: str):
    async def gen():
        yield b": connected\n\n"
        async for chunk in sse_hub.stream(chat_id):
            yield chunk

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)


# ---- Web console (HTML+CSS+JS) ----
@app.get("/console", response_class=HTMLResponse)
def console():
    # raw string (r""") to avoid escaping backticks in JS template literals
    return r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Chat Console · API</title>
<style>
:root{--bg:#0f172a;--card:#111827;--muted:#9ca3af;--text:#e5e7eb;--accent:#22d3ee;--ok:#10b981;--err:#ef4444}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(180deg,#0b1023,#0f172a 40%,#0b1023);
font-family:ui-sans-serif,system-ui,Segoe UI,Roboto,Helvetica,Arial;color:var(--text)}
.wrap{max-width:1200px;margin:24px auto;padding:0 16px}
h1{font-size:22px;margin:16px 0 10px}
.panel{display:grid;grid-template-columns:340px 1fr;gap:16px}
.card{background:rgba(17,24,39,.7);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.06);
border-radius:14px;padding:14px}
label{font-size:12px;color:var(--muted)}
input,textarea,select{width:100%;border:1px solid rgba(255,255,255,.12);background:#0b1023;color:var(--text);
border-radius:10px;padding:10px 12px;font-size:14px;outline:none}
textarea{min-height:72px;resize:vertical}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{cursor:pointer;border:none;border-radius:10px;padding:10px 12px;background:#1f2937;color:#fff}
.btn:hover{background:#374151}
.btn.acc{background:var(--accent);color:#001018;font-weight:700}
.btn.ok{background:var(--ok)}
.btn.err{background:#ef4444}
.small{font-size:12px;color:var(--muted)}
.list{max-height:360px;overflow:auto;border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:8px}
.item{padding:8px;border-bottom:1px dashed rgba(255,255,255,.07)}
.item:last-child{border-bottom:0}
.msg{margin:6px 0;padding:8px;border-radius:10px;background:#0b1023;border:1px solid rgba(255,255,255,.06)}
.msg .meta{color:var(--muted);font-size:12px;margin-bottom:4px}
#stream,#tokens{white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace;background:#0b1023;border:1px solid rgba(255,255,255,.1);border-radius:10px;min-height:60px;padding:10px}
.kv{display:flex;gap:8px;align-items:center}
.kv code{font-size:12px;background:#0b1023;border:1px solid rgba(255,255,255,.1);padding:2px 6px;border-radius:6px}
hr{border:none;border-top:1px solid rgba(255,255,255,.08);margin:12px 0}
.badge{display:inline-block;border:1px solid rgba(255,255,255,.1);padding:2px 6px;border-radius:999px;font-size:11px;color:var(--muted)}
</style>
</head>
<body>
<div class="wrap">
  <h1>Chat Console</h1>
  <div class="panel">

    <!-- Left column: chats management -->
    <div class="card">
      <div class="row">
        <div>
          <label>Title</label>
          <input id="newChatTitle" value="New conversation" />
        </div>
        <div class="kv" style="align-items:end">
          <button class="btn acc" id="createChat">Create</button>
        </div>
      </div>
      <hr/>
      <div class="kv" style="justify-content:space-between">
        <label style="margin:0">Your chats</label>
        <button class="btn" id="listChats">Refresh</button>
      </div>
      <div id="chats" class="list" style="margin-top:8px"></div>
    </div>

    <!-- Right column: conversation -->
    <div class="card">
      <div class="kv" style="justify-content:space-between">
        <div>
          <b id="chatTitle">No chat selected</b>
        <span id="chatIdBadge" class="badge" style="display:none"></span>
        </div>
        <div class="kv">
          <button class="btn ok" id="openStream">Connect SSE</button>
          <button class="btn err" id="closeStream">Close SSE</button>
        </div>
      </div>

      <div id="history" class="list" style="margin-top:8px"></div>

      <hr/>
      <div class="row">
        <div>
          <label>User message</label>
          <textarea id="userMsg" placeholder="Type your message..."></textarea>
        </div>
        <div>
          <label>Idempotency-Key (optional)</label>
          <input id="idem" placeholder="idem-123..." />
          <div style="height:8px"></div>
          <button class="btn acc" id="sendMsg">Send</button>
        </div>
      </div>

      <hr/>
      <div class="row">
        <div>
          <label>Tokens</label>
          <div id="tokens"></div>
        </div>
        <div>
          <label>Status/Result</label>
          <div id="stream"></div>
        </div>
      </div>
    </div>

  </div>
  <div class="small" style="margin-top:10px">Flow: create/select a chat → Connect SSE → send a message.</div>
</div>

<script>
(() => {
  // Safe DOM helpers
  const $id = (id) => document.getElementById(id);
  const safe = (el, name) => {
    if (!el) throw new Error(`Element #${name} not found in DOM`);
    return el;
  };

  // State
  let currentChat = null;
  let es = null;

  // UI helpers
  function logStatus(line) {
    const el = $id("stream");
    if (!el) return;
    el.textContent += (line + "\n");
    el.scrollTop = el.scrollHeight;
  }
  function appendToken(t) {
    const el = $id("tokens");
    if (!el) return;
    el.textContent += t;
    el.scrollTop = el.scrollHeight;
  }
  function notify(msg) {
    console.error(msg);
    logStatus("⚠️ " + msg);
  }
  function renderHeader() {
    const titleEl = $id("chatTitle");
    const badgeEl = $id("chatIdBadge");
    if (!titleEl || !badgeEl) return;
    if (currentChat) {
      titleEl.textContent = currentChat.title || "(untitled)";
      badgeEl.textContent = currentChat.id;
      badgeEl.style.display = "inline-block";
    } else {
      titleEl.textContent = "No chat selected";
      badgeEl.style.display = "none";
    }
  }

  // Views
  function uiChatItem(c) {
    const d = document.createElement("div");
    d.className = "item";
    d.innerHTML = `
      <div><b>${c.title}</b> <span class="small">[${c.id}]</span></div>
      <div class="small">${new Date(c.created_at).toLocaleString()}</div>
      <div class="kv" style="margin-top:6px; gap:6px">
        <button type="button" class="btn" data-action="use">Use</button>
        <button type="button" class="btn" data-action="rename">Rename</button>
        <button type="button" class="btn err" data-action="delete">Delete</button>
      </div>`;
    d.querySelector('[data-action="use"]').onclick = () => selectChat(c);
    d.querySelector('[data-action="rename"]').onclick = async () => {
      const title = prompt("New title", c.title) || c.title;
      try {
        const res = await fetch(`/v1/chats/${encodeURIComponent(c.id)}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title })
        });
        if (!res.ok) return notify("Rename failed");
        await listChats();
        if (currentChat && currentChat.id === c.id) {
          const updated = await res.json();
          currentChat = updated.chat || currentChat;
          renderHeader();
        }
      } catch (e) {
        notify("Network error while renaming");
      }
    };
    d.querySelector('[data-action="delete"]').onclick = async () => {
      if (!confirm("Delete chat?")) return;
      try {
        const res = await fetch(`/v1/chats/${encodeURIComponent(c.id)}`, { method: "DELETE" });
        if (res.status !== 204) return notify("Delete failed");
        if (currentChat && currentChat.id === c.id) {
          closeSSE();
          currentChat = null;
          renderHeader();
          const hist = $id("history");
          if (hist) hist.innerHTML = "";
        }
        listChats();
      } catch (e) {
        notify("Network error while deleting");
      }
    };
    return d;
  }

  function uiMsg(m) {
    const d = document.createElement("div");
    d.className = "msg";
    const safeContent = (m.content || "").replace(/</g, "&lt;");
    d.innerHTML =
      `<div class="meta">${m.role.toUpperCase()} · ${new Date(m.created_at).toLocaleTimeString()} · <code>${m.id}</code></div>` +
      `<div>${safeContent}</div>`;
    return d;
  }

  // API
  async function listChats() {
    try {
      const res = await fetch("/v1/chats");
      if (!res.ok) return notify("Failed to list chats");
      const data = await res.json();
      const box = safe($id("chats"), "chats");
      box.innerHTML = "";
      (data.chats || []).forEach((c) => box.appendChild(uiChatItem(c)));
    } catch (e) {
      notify("Network error while listing chats");
    }
  }

  async function createChat() {
    try {
      const titleInput = safe($id("newChatTitle"), "newChatTitle");
      const title = titleInput.value || "New conversation";
      const res = await fetch("/v1/chats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
      });
      if (res.status !== 201) return notify("Failed to create chat");
      const data = await res.json();
      await listChats();
      await selectChat(data.chat);
    } catch (e) {
      notify("Network error while creating chat");
    }
  }

  async function selectChat(c) {
    currentChat = c;
    renderHeader();
    await loadMsgs();
    openSSE();
  }

  async function loadMsgs() {
    if (!currentChat) return notify("Select a chat");
    try {
      const res = await fetch(`/v1/chats/${encodeURIComponent(currentChat.id)}/messages`);
      if (!res.ok) return notify("Failed to load messages");
      const data = await res.json();
      const box = safe($id("history"), "history");
      box.innerHTML = "";
      (data.messages || []).reverse().forEach((m) => box.appendChild(uiMsg(m)));
    } catch (e) {
      notify("Network error while loading messages");
    }
  }

  async function sendMsg() {
    if (!currentChat) return notify("Select a chat");
    try {
      const ta = safe($id("userMsg"), "userMsg");
      const content = (ta.value || "").trim();
      if (!content) return notify("Type a message");
      const idemEl = $id("idem");
      const headers = { "Content-Type": "application/json" };
      if (idemEl && idemEl.value.trim()) headers["Idempotency-Key"] = idemEl.value.trim();

      const body = { chat_id: currentChat.id, content, meta: { client_ts: new Date().toISOString() } };
      const res = await fetch("/v1/messages", { method: "POST", headers, body: JSON.stringify(body) });
      if (res.status !== 202) return notify("Failed to send message");
      ta.value = "";
      await loadMsgs();
    } catch (e) {
      notify("Network error while sending message");
    }
  }

  // SSE
  function openSSE() {
    if (!currentChat) return notify("Select a chat");
    closeSSE();
    const tokens = $id("tokens");
    const stream = $id("stream");
    if (tokens) tokens.textContent = "";
    if (stream) stream.textContent = "";

    const sseUrl = `/v1/chats/${encodeURIComponent(currentChat.id)}/stream`;
    try {
      es = new EventSource(sseUrl);

      es.addEventListener("status", (e) => logStatus(e.data));
      es.addEventListener("token", (e) => {
        try {
          const { chunk } = JSON.parse(e.data);
          appendToken(chunk || "");
        } catch {
          appendToken(e.data || "");
        }
      });
      es.addEventListener("message", (e) => {
        try {
          JSON.parse(e.data); // final message
          appendToken("\n");
          logStatus("✓ completed");
          loadMsgs();
        } catch {
          logStatus(e.data);
        }
      });
      es.onopen = () => logStatus("[SSE open]");
      es.onerror = () => logStatus("[SSE error]");
    } catch (e) {
      notify("Failed to open SSE");
    }
  }

  function closeSSE() {
    if (es) {
      try { es.close(); } catch {}
      es = null;
      logStatus("[SSE closed]");
    }
  }

  // Bindings
  document.addEventListener("DOMContentLoaded", () => {
    try {
      safe($id("listChats"), "listChats").onclick = listChats;
      safe($id("createChat"), "createChat").onclick = createChat;
      safe($id("sendMsg"), "sendMsg").onclick = sendMsg;
      safe($id("openStream"), "openStream").onclick = openSSE;
      safe($id("closeStream"), "closeStream").onclick = closeSSE;

      listChats();
      renderHeader();
    } catch (e) {
      console.error(e);
      notify("Missing elements in the console HTML. Check ids.");
    }
  });
})();
</script>
</body></html>
    """


@app.get("/", response_class=HTMLResponse)
def index():
    return """<html><body style="font-family:system-ui;padding:20px">
    <h2>User↔Server Chat API</h2>
    <p>Web console: <a href="/console">/console</a></p>
    <ul>
      <li>GET /v1/chats</li>
      <li>POST /v1/chats</li>
      <li>PATCH /v1/chats/{chat_id}</li>
      <li>DELETE /v1/chats/{chat_id}</li>
      <li>GET /v1/chats/{chat_id}/messages</li>
      <li>POST /v1/messages</li>
      <li>GET /v1/chats/{chat_id}/stream (SSE)</li>
    </ul>
    </body></html>"""
