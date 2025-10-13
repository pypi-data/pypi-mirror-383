# tests/conftest.py
from __future__ import annotations

import os
import socket
import time
import subprocess
from urllib import request
from typing import Optional

import pytest

# -------- Default logging config --------
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("LOG_JSON", "true")

# -------- Endpoints / ports --------
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = int(os.getenv("PGPORT", "55432"))
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASS = os.getenv("PGPASSWORD", "postgres")
PG_DB = os.getenv("PGDATABASE", "postgres")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Ollama (presence check only; do NOT start or pull models)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
RAG_MODEL = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text:latest")


# -------- Helpers --------
def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """Return True if TCP connect succeeds within timeout."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False


def _wait_pg_ready(max_wait: float = 30.0) -> bool:
    """
    Wait until PostgreSQL is reachable and responds to a simple query.
    Returns True if ready before deadline, otherwise False.
    """
    try:
        import psycopg  # noqa: F401
    except Exception:
        return False

    dsn = f"user={PG_USER} password={PG_PASS} dbname={PG_DB} host={PG_HOST} port={PG_PORT}"
    deadline = time.monotonic() + max_wait
    last_err: Optional[Exception] = None

    while time.monotonic() < deadline:
        if not _port_open(PG_HOST, PG_PORT, 0.3):
            time.sleep(0.3)
            continue
        try:
            import psycopg
            with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                _ = cur.fetchone()
            return True
        except Exception as ex:
            last_err = ex
            time.sleep(0.4)

    if last_err:
        print(f"[conftest] Postgres not ready: {last_err!r}")
    return False


def _wait_qdrant_ready(max_wait: float = 30.0) -> bool:
    """
    Wait until Qdrant REST endpoint is reachable and returns HTTP 200.
    Returns True if ready before deadline, otherwise False.
    """
    deadline = time.monotonic() + max_wait
    url = f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections"
    last_err: Optional[Exception] = None

    while time.monotonic() < deadline:
        if not _port_open(QDRANT_HOST, QDRANT_PORT, 0.3):
            time.sleep(0.3)
            continue
        try:
            with request.urlopen(url, timeout=2.0) as resp:
                if resp.status == 200:
                    return True
        except Exception as ex:
            last_err = ex
            time.sleep(0.4)

    if last_err:
        print(f"[conftest] Qdrant not ready: {last_err!r}")
    return False


def _ollama_available(timeout: float = 2.0) -> bool:
    """
    Return True if the Ollama server responds to /api/tags with HTTP 200.
    """
    if not _port_open(OLLAMA_HOST, OLLAMA_PORT, timeout):
        return False
    try:
        with request.urlopen(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


# -------- Logger init --------
@pytest.fixture(scope="session", autouse=True)
def _init_logger_once():
    """Initialize the shared LogBus exactly once per test session."""
    from convo_orchestrator.shared import LogBus

    LogBus.instance()
    yield


# -------- Service orchestration: Postgres and Qdrant only --------
@pytest.fixture(scope="session", autouse=True)
def maybe_start_pg_qdrant_only():
    """
    Conditionally start Postgres and Qdrant with docker compose if their local
    ports are not in use. Verifies the health of both services.

    Ollama is NOT started and no model pulls are performed.
    """
    started_any = False

    # In CI, we assume services are pre-provisioned; just wait for readiness.
    if os.getenv("CI") == "true":
        if not _wait_pg_ready(40.0):
            raise RuntimeError("Postgres is not ready in CI")
        if not _wait_qdrant_ready(40.0):
            raise RuntimeError("Qdrant is not ready in CI")
        yield
        return

    # Check if Docker is available; if not, require local services to be ready.
    try:
        subprocess.run(["docker", "ps"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        if not _wait_pg_ready(40.0):
            raise RuntimeError("Postgres is not reachable and Docker is not available to start it")
        if not _wait_qdrant_ready(40.0):
            raise RuntimeError("Qdrant is not reachable and Docker is not available to start it")
        yield
        return

    # Postgres
    if not _port_open(PG_HOST, PG_PORT):
        subprocess.run(["docker", "compose", "up", "-d", "postgres"], check=False)
        started_any = True
    if not _wait_pg_ready(40.0):
        raise RuntimeError("Postgres is not reachable")

    # Qdrant
    if not _port_open(QDRANT_HOST, QDRANT_PORT):
        subprocess.run(["docker", "compose", "up", "-d", "qdrant"], check=False)
        started_any = True
    if not _wait_qdrant_ready(40.0):
        raise RuntimeError("Qdrant is not reachable")

    # Export effective env vars for tests
    os.environ["PGHOST"] = PG_HOST
    os.environ["PGPORT"] = str(PG_PORT)
    os.environ["PGUSER"] = PG_USER
    os.environ["PGPASSWORD"] = PG_PASS
    os.environ["PGDATABASE"] = PG_DB
    os.environ["QDRANT_HOST"] = QDRANT_HOST
    os.environ["QDRANT_PORT"] = str(QDRANT_PORT)

    try:
        yield
    finally:
        if started_any:
            subprocess.run(["docker", "compose", "down"], check=False)


# -------- Strict Ollama presence check (NOT started automatically) --------
@pytest.fixture(scope="session", autouse=True)
def assert_ollama_present_or_fail():
    """
    Some tests may require embeddings via Ollama.
    We do not start it automatically nor pull models; if it is not reachable,
    fail the suite with a clear error.
    """
    if not _ollama_available():
        raise RuntimeError(
            "Ollama is not reachable at "
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}. "
            "It is not started automatically; start it externally or adjust the tests."
        )
    yield
