# examples/networking.py
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
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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

# Summarization / context
CTX_WINDOW_CHARS = int(os.getenv("CTX_WINDOW_CHARS", "1500"))
CTX_MARGIN_CHARS = int(os.getenv("CTX_MARGIN_CHARS", "150"))

# Retrieval/Search
TOPK_OPTIONS = int(os.getenv("TOPK_OPTIONS", "5"))
Q_COLL = os.getenv("RAG_Q_COLLECTION", "rag_example_ops")
PG_TABLE = os.getenv("RAG_PG_TABLE", "rag_docs_ops")

# ===================== RAG adapters =====================
from convo_orchestrator.adapters.postgres_lexical import PostgresLexicalStore
from convo_orchestrator.adapters.qdrant_store import QdrantVectorStore
from convo_orchestrator.adapters.encoder_ollama import OllamaEncoder
from convo_orchestrator.application.selection_service import (
    SelectionOptions,
    decide_exact_options_none,
)
from convo_orchestrator import (
    Event,
    EventId,
    EventManager,
    HandlerRegistry,
    InMemoryEventRepository,
    InMemoryMetrics,
    Policy,
    SystemClock,
)

# ===================== Utilities =====================
def _norm(s: str | None) -> str:
    """Lowercase, trim, and collapse whitespace."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _tok(s: str | None) -> list[str]:
    """Tokenize by whitespace after normalization."""
    return _norm(s).split()


def _token_groups(term: str) -> list[set[str]]:
    """
    Split tokens; tokens containing '/' are treated as OR groups.
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


def _join_msgs(msgs: List[Dict[str, Any]]) -> str:
    """Join messages into a plain text conversation block."""
    return " \n".join(f"{m['role']}: {m['content']}" for m in msgs)


# ===================== INTENT & RESPONSE Prompts =====================
INTENT_PROMPT = """\
<|begin_of_system|>
You are a classifier for a network engineer chat.

Task:
1) Decide whether the user shows TECHNICAL INTENT (asking for actions/commands) and the conversation is NOT closed.
2) If YES, extract the referenced commands (simple or composite) as short intent strings, e.g.:
   "list devices", "show interface status", "lab topology", "bgp summary". Do not hallucinate.

Output:
- If NO technical intent → empty JSON: {}
- If YES technical intent → {"commands": ["<cmd 1>", "<cmd 2>", "..."]}

Rules:
- Return STRICT, VALID JSON only (no extra text).

SUMMARY:
{summary_block}

HISTORY (excluding the latest user message):
{history_block}

USER MESSAGE:
{latest_user}
<|end_of_system|>
"""

RESPONSE_PROMPT = """\
<|begin_of_system|>
You are a network engineer assistant. Decide WHICH commands to run and WHY,
based on:
- SUMMARY (history of relevant commands)
- Recent HISTORY (excluding the latest user message)
- FOUND COMMANDS (valid options from the index)
- USER MESSAGE

Rules:
1) Use the context. If any required parameter is missing (e.g., lab_id, device_id, interface), ask briefly for it.
2) Do NOT invent commands beyond FOUND COMMANDS.
3) Return STRICT JSON only:
   {
     "response": "<explain what you will execute and why>",  // ALWAYS a non-empty string.
     "commands": ["<op_id or alias>", "..."] | null
   }
4) If FOUND COMMANDS is "(empty)", ask a short clarification or state you cannot determine commands.

FOUND COMMANDS:
{context_block}

HISTORY:
{history_block}

SUMMARY:
{summary_block}

MESSAGE:
User: {latest_user}
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
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
        )


# ===================== Infra (DB) =====================
def pg_conn():
    """Open a psycopg connection with autocommit."""
    return psycopg.connect(PG_DSN, autocommit=True)


def ensure_tables():
    """Create minimal schema for chats/messages, idempotency, RAG corpus, and command catalog."""
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

        # RAG corpus (ops)
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

        # Commands catalog (instead of products)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS ops (
            id TEXT PRIMARY KEY,              -- op_id
            title TEXT NOT NULL,
            description TEXT,
            phrases TEXT[],                   -- user_phrases
            requirements TEXT[],              -- hard_requirements
            params JSONB,                     -- list of {name, required, ...}
            notes TEXT[],
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );"""
        )
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ops_title_trgm ON ops USING GIN (title gin_trgm_ops);"
            )
        except Exception:
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ops_title_lower_idx ON ops (LOWER(title));"
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


def reindex_ops_into_rag(rows: List[Dict[str, Any]]) -> None:
    """Index provided ops rows into Postgres lexical table and Qdrant vector store."""
    if not rows:
        return
    pg_items, vec_items = [], []
    for r in rows:
        op_id = r["id"]
        title = (r.get("title") or "").strip()
        desc = (r.get("description") or "").strip()
        phrases = r.get("phrases") or []
        joined_phrases = "; ".join(phrases) if isinstance(phrases, list) else str(phrases or "")
        text = f"{title}. {desc} Phrases: {joined_phrases}".strip()
        meta = {"id": op_id, "name": title, "description": desc}
        pg_items.append((op_id, text, meta))
        vec_items.append((op_id, encoder.embed(text), meta))
    assert lex.upsert_many(pg_items).is_ok()
    assert vec.upsert_many(vec_items).is_ok()


def upsert_ops_pg(rows: List[Dict[str, Any]]) -> None:
    """Upsert ops rows into the ops table."""
    if not rows:
        return
    with pg_conn() as conn, conn.cursor() as cur:
        for r in rows:
            cur.execute(
                """INSERT INTO ops (id,title,description,phrases,requirements,params,notes)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)
                           ON CONFLICT (id) DO UPDATE
                           SET title=EXCLUDED.title,description=EXCLUDED.description,
                               phrases=EXCLUDED.phrases,requirements=EXCLUDED.requirements,
                               params=EXCLUDED.params,notes=EXCLUDED.notes
            """,
                (
                    r.get("id"),
                    r.get("title"),
                    r.get("description"),
                    r.get("phrases"),
                    r.get("requirements"),
                    json.dumps(r.get("params") or []),
                    r.get("notes"),
                ),
            )


def upsert_ops_and_index(rows: List[Dict[str, Any]]) -> None:
    """Upsert ops then index them into both stores."""
    upsert_ops_pg(rows)
    reindex_ops_into_rag(rows)


def _seed_demo_ops() -> list[dict]:
    """Seed a minimal set of demo operations (ops) for the catalog and RAG index."""

    def row(op_id, title, primary_intent, user_phrases, hard_requirements, parameters, notes):
        desc = primary_intent
        return {
            "id": op_id,
            "title": title,
            "description": desc,
            "phrases": user_phrases,
            "requirements": hard_requirements,
            "params": parameters,
            "notes": notes,
        }

    demo: list[dict] = []
    demo.append(
        row(
            "list_devices",
            "IP/Inventory → List devices",
            "List devices from IP inventory optionally filtered by lab_id/text",
            [
                "ip inventory list devices",
                "devices in ip lab",
                "find device by name in ip",
                "inventario ip devices",
                "devices index ip",
            ],
            [],
            [
                {"name": "lab_id", "required": False},
                {"name": "q", "required": False},
                {"name": "page", "required": False},
                {"name": "limit", "required": False},
            ],
            [
                "Backed by views.yaml::devices_index (fields: id, labels.node_name, labels.lab_id, vendor, capabilities).",
                "Executor type: inventory_view.",
            ],
        )
    )
    demo.append(
        row(
            "show_interfaces_brief",
            "Interfaces → Brief (IOS-XR)",
            "quick up/down/admin overview",
            ["show interfaces brief", "interfaces brief table"],
            ["You must provide lab_id and device_id."],
            [{"name": "lab_id", "required": True}, {"name": "device_id", "required": True}],
            ["Shows Intf | Intf State | LineP State | Encap | MTU | BW."],
        )
    )
    demo.append(
        row(
            "show_interfaces_all",
            "Interfaces → All (IOS-XR)",
            "deep interface audit (counters/rates/errors)",
            ["show interfaces all", "all interfaces full detail"],
            ["You must provide lab_id and device_id."],
            [{"name": "lab_id", "required": True}, {"name": "device_id", "required": True}],
            [],
        )
    )
    demo.append(
        row(
            "eve_lab_topology",
            "EVE-NG → Lab topology",
            "fetch topology.json (nodes, links, networks)",
            ["get eve topology", "eve_ng topology.json"],
            ["You must provide lab_id."],
            [{"name": "lab_id", "required": True}],
            [],
        )
    )
    demo.append(
        row(
            "show_bgp_summary",
            "BGP → Summary",
            "overall BGP health snapshot per AFI/SAFI",
            ["show bgp summary", "show bgp ipv4 unicast summary"],
            ["You must provide lab_id and device_id."],
            [
                {"name": "lab_id", "required": True},
                {"name": "device_id", "required": True},
                {"name": "afi", "required": False, "default": ""},
                {"name": "safi", "required": False, "default": ""},
            ],
            [],
        )
    )
    demo.append(
        row(
            "list_labs",
            "IP/Inventory → List labs",
            "List registered E2E labs in IP service inventory",
            [
                "ip inventory list labs",
                "show labs in ip inventory",
                "what labs do we have in ip",
                "inventario ip labs",
                "labs index ip",
            ],
            [],
            [
                {"name": "page", "required": False},
                {"name": "limit", "required": False},
                {"name": "q", "required": False},
            ],
            [
                "Backed by views.yaml::labs_index (fields: id, attrs.lab_name).",
                "Executor type: inventory_view.",
            ],
        )
    )
    demo.append(
        row(
            "show_lacp_bundle",
            "LACP → By bundle (scoped)",
            "verify LACP state for a bundle",
            ["show lacp Bundle-Ether15", "lacp bundle"],
            ["You must provide lab_id, device_id and bundle."],
            [
                {"name": "lab_id", "required": True},
                {"name": "device_id", "required": True},
                {"name": "bundle", "required": True},
            ],
            [],
        )
    )
    return demo


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
    """CRUD for chat entities."""

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
                        "message": "At least one of title or metadata must be provided",
                    }
                },
            )
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(
                    404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}}
                )
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
                raise HTTPException(
                    404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}}
                )


class MessageService:
    """Persistence for messages (user/server)."""

    def create_user_message(self, chat_id: str, content: str, meta: Optional[Dict[str, Any]]) -> Message:
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(
                    404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}}
                )
            mid = f"msg_usr_{uuid.uuid4().hex[:8]}"
            cur.execute(
                """INSERT INTO messages(id,chat_id,role,content,meta)
                           VALUES(%s,%s,'user',%s,%s)
                           RETURNING id,chat_id,role,content,created_at,meta""",
                (mid, chat_id, content, json.dumps(meta) if meta is not None else None),
            )
            r = cur.fetchone()
        return Message(
            id=r[0],
            chat_id=r[1],
            role=r[2],
            content=r[3],
            created_at=r[4].isoformat() + "Z",
            meta=r[5],
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
            id=r[0],
            chat_id=r[1],
            role=r[2],
            content=r[3],
            created_at=r[4].isoformat() + "Z",
            meta=r[5],
        )

    def list(self, chat_id: str, limit: int = 50, before: Optional[str] = None) -> MessagesListResponse:
        with pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE id=%s", (chat_id,))
            if not cur.fetchone():
                raise HTTPException(
                    404, detail={"error": {"code": "NOT_FOUND", "message": "Chat not found"}}
                )
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
                id=r[0],
                chat_id=r[1],
                role=r[2],
                content=r[3],
                created_at=r[4].isoformat() + "Z",
                meta=r[5],
            )
            for r in rows
        ]
        next_cursor = rows[-1][0] if rows and len(rows) == limit else None
        return MessagesListResponse(messages=msgs, next_cursor=next_cursor)


# ===================== Orchestrator (OO) =====================
class RAGOrchestrator:
    """Coordinates intent detection, retrieval, response planning, and SSE emission."""

    def __init__(self):
        self.llm = OllamaLLM(model=GEN_MODEL)

    def get_latest_summary(self, chat_id: str) -> Tuple[str, Optional[str]]:
        """Return (summary_text, upto_msg_id) if exists for a chat."""
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
        """List all messages in chronological order; optionally exclude one by id."""
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
        return [
            {"id": r[0], "role": r[1], "content": r[2], "ts": r[3].isoformat() + "Z"} for r in rows
        ]

    def maybe_summarize(self, chat_id: str) -> None:
        """Summarize the conversation if it exceeds the character window + margin."""
        msgs = self.list_messages_all(chat_id)
        if not msgs:
            return
        prev_summary, _prev_upto = self.get_latest_summary(chat_id)
        text_all = (prev_summary + "\n" + _join_msgs(msgs)).strip()
        if len(text_all) <= CTX_WINDOW_CHARS + CTX_MARGIN_CHARS:
            return
        upto_id = msgs[-1]["id"]
        # Command-oriented summary
        prompt = f"""\
<|begin_of_system|>
Summarize the network engineer ↔ assistant conversation focusing on the HISTORY OF RELEVANT COMMANDS
(already executed or agreed), key parameters (lab_id, device_id, interface, afi/safi, etc.), and any open questions.
Maximum {CTX_WINDOW_CHARS} characters. Plain, concise English text.
<|end_of_system|>

PREVIOUS SUMMARY:
{prev_summary}

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
        """Collect recent history and the latest summary, preferring messages after the last summary."""
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
        """Build the prompt used by the classifier to detect technical intent."""
        history, (summary_text, _upto) = self._collect_history(chat_id, exclude_id=latest_user_id)
        history_block = "\n".join([f"{m['role']}: {m['content']}" for m in history]) if history else "(empty)"
        return INTENT_PROMPT.format(
            summary_block=summary_text or "(empty)",
            history_block=history_block,
            latest_user=latest_user_text,
        )

    def parse_intent_json(self, raw: str) -> Dict[str, Any]:
        """Parse classifier output as JSON, returning {} or {'commands': [...] }."""
        try:
            data = json.loads(raw) if raw else {}
            if isinstance(data, dict):
                if "commands" in data:
                    cmds = data.get("commands")
                    if isinstance(cmds, list):
                        return {"commands": [str(x).strip() for x in cmds if str(x).strip()]}
                    return {"commands": []}
                else:
                    return {}
        except Exception as ex:
            print("[intent.parse.error]", ex, raw[:200])
        return {}

    def find_ops_for_terms(self, terms: List[str], topk_per_term: int = TOPK_OPTIONS) -> List[Dict[str, str]]:
        """
        For each term, decide EXACT/OPTIONS/NONE using the selection service.
        Returns a list of allowed ops: [{'id': op_id, 'name': title}, ...]
        """
        if not terms:
            return []
        out: Dict[str, str] = {}

        for original in terms:
            term = _norm(original)
            if not term:
                continue

            sel = decide_exact_options_none(
                term,
                lex_store=lex,
                vec_store=vec,
                encoder=encoder,
                opts=SelectionOptions(
                    top_k_options=topk_per_term, exact_cover=1.0, options_min_cover=0.0
                ),
            )

            if sel.outcome.value == "exact":
                did = sel.context
                if not did:
                    continue
                # Try to fetch the official title if available
                try:
                    with pg_conn() as conn, conn.cursor() as cur:
                        cur.execute("SELECT title FROM ops WHERE id=%s LIMIT 1", (did,))
                        row = cur.fetchone()
                    out[did] = (row[0] if row else did)
                except Exception:
                    out.setdefault(did, did)

            elif sel.outcome.value == "options":
                for cand in sel.context or []:
                    did = cand.get("doc_id")
                    name = cand.get("name") or did
                    if did:
                        out.setdefault(did, name)

        return [{"id": k, "name": v} for k, v in out.items()]

    def build_response_prompt(
        self,
        chat_id: str,
        latest_user_text: str,
        latest_user_id: Optional[str],
        allowed_ops: List[Dict[str, str]],
    ) -> str:
        """Build the planning prompt to explain and list commands to execute."""
        history, (summary_text, _) = self._collect_history(chat_id, exclude_id=latest_user_id)
        context_block = (
            "\n".join([f"- ({p['id']}) {p['name']}" for p in allowed_ops]) if allowed_ops else "(empty)"
        )
        history_block = "\n".join([f"{m['role']}: {m['content']}" for m in history]) if history else "(empty)"
        return RESPONSE_PROMPT.format(
            context_block=context_block,
            history_block=history_block,
            summary_block=summary_text or "(empty)",
            latest_user=latest_user_text,
        )

    def _safe_parse_llm_json(self, raw: str) -> Dict[str, Any]:
        """Parse LLM JSON; attempt to recover if extra text surrounds the JSON object."""
        base = {"response": "", "commands": None}
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
            "commands": data.get("commands"),
        }
        if isinstance(out["commands"], list) and not out["commands"]:
            out["commands"] = None
        return out

    def sanitize_llm_output(self, data: Dict[str, Any], allowed_ops: List[Dict[str, str]]) -> Dict[str, Any]:
        """Enforce that commands are among allowed ops (by id or exact title match)."""
        allowed_ids = {p["id"] for p in allowed_ops}
        resp = data.get("response")
        resp = resp if isinstance(resp, str) else ""
        data["response"] = resp.strip()

        valid_cmds: List[str] = []
        cmds = data.get("commands")
        if isinstance(cmds, list):
            for it in cmds:
                if not isinstance(it, str):
                    continue
                it_norm = _norm(it)
                if it in allowed_ids:
                    valid_cmds.append(it)
                else:
                    # match by normalized title
                    for op in allowed_ops:
                        if _norm(op["name"]) == it_norm:
                            valid_cmds.append(op["id"])
                            break
        data["commands"] = valid_cmds if valid_cmds else None

        if not allowed_ops:
            data["commands"] = None
        return data

    async def process_user_message(self, msg: Message, sse_notifier: "SSEHub"):
        """End-to-end orchestration for a newly posted user message."""
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

        terms = intent.get("commands", []) if isinstance(intent, dict) else []
        allowed_ops = self.find_ops_for_terms(terms, topk_per_term=TOPK_OPTIONS)

        resp_prompt = self.build_response_prompt(
            chat_id, msg.content, latest_user_id=msg.id, allowed_ops=allowed_ops
        )
        print("[llm.resp_prompt]", resp_prompt)
        raw = self.llm.complete_json(resp_prompt, temperature=0.0)
        data = self.sanitize_llm_output(self._safe_parse_llm_json(raw), allowed_ops)
        print("[llm.raw]", raw)

        text = data.get("response", "").strip()
        meta = {"model": GEN_MODEL, "allowed_ops": allowed_ops, "commands": data.get("commands")}
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
    """Minimal in-memory SSE hub keyed by chat_id."""

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
        """Async generator of SSE chunks for a chat."""
        q = await self.subscribe(chat_id)
        try:
            # initial heartbeat
            yield b": ping\n\n"
            while True:
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=10.0)
                    ev = payload.get("event", "message")
                    data = payload.get("data", {})
                    ev_id = f"ev_{uuid.uuid4().hex[:6]}"
                    # Always format as proper SSE (event, id, data)
                    yield f"event: {ev}\n".encode()
                    yield f"id: {ev_id}\n".encode()
                    yield ("data: " + json.dumps(data, ensure_ascii=False) + "\n\n").encode()
                except asyncio.TimeoutError:
                    # periodic heartbeat (prevents timeouts and flushes)
                    yield b": ping\n\n"
        finally:
            self.unsubscribe(chat_id, q)


# ===================== Idempotency =====================
class Idempotency:
    """Simple idempotency helper based on a caller-provided key."""

    @staticmethod
    def _hash_body(obj: Any) -> str:
        return hashlib.sha256(
            json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def check_and_store(
        key: str, body: Dict[str, Any], response: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
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
    scheduler_tick_ms=200,  # adequate for AT/interval
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


# Register handler and event
_handler_registry.register("chat-reply", _handle_reply)

_reply_event = Event(
    id=REPLY_EVENT_ID,
    name="chat-reply",
    handler_name="chat-reply",  # reference to handler name
    policy=Policy(timeout_sec=90.0, max_retries=0, max_concurrency=1),
    active=True,
)
_event_repo.save_event(_reply_event)

# ===================== App & Routes =====================
app = FastAPI(
    title="User↔Server Chat API",
    version="1.0.0",
    description="REST + SSE API for multi-chat",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_svc = ChatService()
msg_svc = MessageService()
orchestrator = RAGOrchestrator()
sse_hub = SSEHub()


@app.on_event("startup")
def _startup():
    ensure_tables()
    try:
        upsert_ops_and_index(_seed_demo_ops())
        print("[startup] Seeded + indexed demo ops")
    except Exception as ex:
        print("[startup] seed/index failed:", ex)

    # Start the event manager
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

    # Notify SSE clients that the job is queued
    asyncio.create_task(sse_hub.emit(msg.chat_id, {"event": "status", "data": {"state": "queued"}}))

    async def _emit_later():
        try:
            print(f"[emit_later] will emit in 60s for chat={msg.chat_id} msg={msg.id}")
            await asyncio.sleep(60.0)
            res = await event_mgr.emit(
                REPLY_EVENT_ID, payload={"chat_id": msg.chat_id, "message_id": msg.id}
            )
            if res.is_ok():
                print(f"[emit_later] emitted job → {REPLY_EVENT_ID.value}")
            else:
                print(f"[emit_later] emit failed: {res}")
                await sse_hub.emit(
                    msg.chat_id, {"event": "status", "data": {"state": "error", "detail": "emit failed"}}
                )
        except Exception as ex:
            print("[emit_later.error]", ex)
            await sse_hub.emit(
                msg.chat_id, {"event": "status", "data": {"state": "error", "detail": str(ex)}}
            )

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

    <!-- Left column: chat management -->
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
  const $id = (id) => document.getElementById(id);
  const safe = (el, name) => { if (!el) throw new Error(`Element #${name} not found in DOM`); return el; };

  let currentChat = null;
  let es = null;

  function logStatus(line) {
    const el = $id("stream"); if (!el) return;
    el.textContent += (line + "\n"); el.scrollTop = el.scrollHeight;
  }
  function appendToken(t) {
    const el = $id("tokens"); if (!el) return;
    el.textContent += t; el.scrollTop = el.scrollHeight;
  }
  function notify(msg) { console.error(msg); logStatus("⚠️ " + msg); }
  function renderHeader() {
    const titleEl = $id("chatTitle"); const badgeEl = $id("chatIdBadge");
    if (!titleEl || !badgeEl) return;
    if (currentChat) { titleEl.textContent = currentChat.title || "(untitled)"; badgeEl.textContent = currentChat.id; badgeEl.style.display = "inline-block"; }
    else { titleEl.textContent = "No chat selected"; badgeEl.style.display = "none"; }
  }

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
        const res = await fetch(`/v1/chats/${encodeURIComponent(c.id)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }) });
        if (!res.ok) return notify("Rename failed");
        await listChats();
        if (currentChat && currentChat.id === c.id) { const updated = await res.json(); currentChat = updated.chat || currentChat; renderHeader(); }
      } catch (e) { notify("Network error while renaming"); }
    };
    d.querySelector('[data-action="delete"]').onclick = async () => {
      if (!confirm("Delete chat?")) return;
      try {
        const res = await fetch(`/v1/chats/${encodeURIComponent(c.id)}`, { method: "DELETE" });
        if (res.status !== 204) return notify("Delete failed");
        if (currentChat && currentChat.id === c.id) { closeSSE(); currentChat = null; renderHeader(); const hist = $id("history"); if (hist) hist.innerHTML = ""; }
        listChats();
      } catch (e) { notify("Network error while deleting"); }
    };
    return d;
  }

  function uiMsg(m) {
    const d = document.createElement("div");
    d.className = "msg";
    const safeContent = (m.content || "").replace(/</g, "&lt;");
    d.innerHTML = `<div class="meta">${m.role.toUpperCase()} · ${new Date(m.created_at).toLocaleTimeString()} · <code>${m.id}</code></div>` + `<div>${safeContent}</div>`;
    return d;
  }

  async function listChats() {
    try {
      const res = await fetch("/v1/chats");
      if (!res.ok) return notify("Failed to list chats");
      const data = await res.json();
      const box = safe($id("chats"), "chats");
      box.innerHTML = "";
      (data.chats || []).forEach((c) => box.appendChild(uiChatItem(c)));
    } catch (e) { notify("Network error while listing chats"); }
  }

  async function createChat() {
    try {
      const titleInput = safe($id("newChatTitle"), "newChatTitle");
      const title = titleInput.value || "New conversation";
      const res = await fetch("/v1/chats", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }) });
      if (res.status !== 201) return notify("Failed to create chat");
      const data = await res.json();
      await listChats();
      await selectChat(data.chat);
    } catch (e) { notify("Network error while creating chat"); }
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
    } catch (e) { notify("Network error while loading messages"); }
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
    } catch (e) { notify("Network error while sending message"); }
  }

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
        try { const { chunk } = JSON.parse(e.data); appendToken(chunk || ""); }
        catch { appendToken(e.data || ""); }
      });
      es.addEventListener("message", (e) => {
        try { JSON.parse(e.data); appendToken("\n"); logStatus("✓ completed"); loadMsgs(); }
        catch { logStatus(e.data); }
      });
      es.onopen = () => logStatus("[SSE open]");
      es.onerror = () => logStatus("[SSE error]");
    } catch (e) { notify("Failed to open SSE"); }
  }

  function closeSSE() {
    if (es) { try { es.close(); } catch {} es = null; logStatus("[SSE closed]"); }
  }

  document.addEventListener("DOMContentLoaded", () => {
    try {
      safe($id("listChats"), "listChats").onclick = listChats;
      safe($id("createChat"), "createChat").onclick = createChat;
      safe($id("sendMsg"), "sendMsg").onclick = sendMsg;
      safe($id("openStream"), "openStream").onclick = openSSE;
      safe($id("closeStream"), "closeStream").onclick = closeSSE;
      listChats();
      renderHeader();
    } catch (e) { console.error(e); notify("Missing elements in the console HTML. Check element ids."); }
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
