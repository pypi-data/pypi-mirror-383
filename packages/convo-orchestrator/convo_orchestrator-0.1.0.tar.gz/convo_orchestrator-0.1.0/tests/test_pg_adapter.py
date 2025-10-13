from __future__ import annotations

import asyncio
import os
import pytest

from convo_orchestrator import (
    InMemoryEventRepository,
    InMemoryMetrics,
    SystemClock,
    EventManager,
    HandlerRegistry,
    Event, EventId,
    Trigger, TriggerId, TriggerKind,
    Policy, JobStatus,
)
from convo_orchestrator.adapters.postgres_notify import PostgresNotifyAdapter
from convo_orchestrator.shared import get_logger

log = get_logger("tests.pg.adapter")

REQUIRED_ENV = ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]


def _ensure_env_defaults(monkeypatch) -> None:
    monkeypatch.setenv("PGHOST", os.getenv("PGHOST", "localhost"))
    monkeypatch.setenv("PGPORT", os.getenv("PGPORT", "55432"))
    monkeypatch.setenv("PGUSER", os.getenv("PGUSER", "postgres"))
    monkeypatch.setenv("PGPASSWORD", os.getenv("PGPASSWORD", "postgres"))
    monkeypatch.setenv("PGDATABASE", os.getenv("PGDATABASE", "postgres"))
    log.debug("Env defaults ensured", extra={
        "PGHOST": os.getenv("PGHOST"),
        "PGPORT": os.getenv("PGPORT"),
        "PGUSER": os.getenv("PGUSER"),
        "PGDATABASE": os.getenv("PGDATABASE"),
    })


async def _wait_pg_ready(timeout=15.0) -> bool:
    try:
        import asyncpg
    except Exception:
        pytest.skip("asyncpg not installed; pg adapter test skipped")
    cfg = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "55432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "postgres"),
        "database": os.getenv("PGDATABASE", "postgres"),
    }
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    last_err = None
    log.debug("Waiting for Postgres readiness", extra={"timeout_sec": timeout, "cfg": {**cfg, "password": "***"}})
    while loop.time() < deadline:
        try:
            conn = await asyncpg.connect(**cfg)
            await conn.close()
            log.debug("Postgres is ready")
            return True
        except Exception as ex:
            last_err = ex
            await asyncio.sleep(0.5)
    log.debug("Postgres NOT ready", exc=last_err)
    return False


@pytest.mark.asyncio
async def test_pg_notify_from_table_insert_with_condition(monkeypatch):
    """
    Realistic test: a PostgreSQL trigger does NOTIFY on channel 'chat_events'
    only when inserted rows satisfy a condition (kind='message' AND priority>=5).
    The adapter should emit a job carrying the JSON row as payload.
    """
    _ensure_env_defaults(monkeypatch)
    for k in REQUIRED_ENV:
        assert os.getenv(k), f"{k} must be set for pg adapter test"

    if not await _wait_pg_ready(timeout=20.0):
        pytest.skip("Postgres is not reachable; ensure docker-compose is up")

    # --- Arrange domain/app
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    seen: list[dict] = []

    def handler(ctx):
        seen.append(ctx.payload)
        log.debug("Handler executed", extra={"event_id": ctx.event_id.value, "payload": ctx.payload})
        return "ok"

    registry.register("h", handler)

    ev = Event(
        id=EventId("ev-pg-insert"),
        name="pg-insert",
        handler_name="h",
        policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug("Event saved", extra={"event_id": ev.id.value, "handler": ev.handler_name})

    # EXTERNAL trigger bound to channel 'chat_events'
    trig = Trigger(
        id=TriggerId("chat_events"),
        kind=TriggerKind.EXTERNAL,
        active=True,
    )
    assert repo.attach_trigger(ev.id, trig).is_ok()
    log.debug("Trigger attached", extra={"event_id": ev.id.value, "trigger_id": trig.id.value, "kind": trig.kind})

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics, scheduler_tick_ms=50)
    mgr.start()
    log.debug("EventManager started")

    adapter = PostgresNotifyAdapter(manager=mgr, repo=repo)
    await adapter.start()
    log.debug("PostgresNotifyAdapter started")

    # --- DB: create table + trigger that NOTIFY only when condition matches
    import asyncpg
    conn = await asyncpg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "55432")),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        database=os.getenv("PGDATABASE", "postgres"),
    )
    log.debug("Connected to PG for DDL")

    # DDL: table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_events (
            id SERIAL PRIMARY KEY,
            kind TEXT NOT NULL,
            text TEXT,
            priority INT DEFAULT 0
        );
    """)
    log.debug("Table ensured", extra={"table": "chat_events"})

    # Function that NOTIFY when condition holds
    await conn.execute("""
        CREATE OR REPLACE FUNCTION notify_chat_events() RETURNS trigger AS $$
        BEGIN
            IF NEW.kind = 'message' AND NEW.priority >= 5 THEN
                PERFORM pg_notify('chat_events', row_to_json(NEW)::text);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    log.debug("Trigger function created", extra={"fn": "notify_chat_events"})

    # Trigger
    await conn.execute("DROP TRIGGER IF EXISTS chat_events_notify ON chat_events;")
    await conn.execute("""
        CREATE TRIGGER chat_events_notify
        AFTER INSERT ON chat_events
        FOR EACH ROW
        EXECUTE FUNCTION notify_chat_events();
    """)
    log.debug("Trigger created", extra={"trigger": "chat_events_notify"})

    # --- Insert that should NOT trigger (priority too low)
    log.debug("Inserting row that SHOULD NOT notify")
    await conn.execute(
        "INSERT INTO chat_events(kind, text, priority) VALUES($1, $2, $3);",
        "message", "ignored-low-priority", 1
    )

    await asyncio.sleep(0.2)
    log.debug("Post-insert check (no-notify expected)", extra={"seen": seen})
    assert seen == [], "No notification expected for priority < 5"

    # --- Insert that SHOULD trigger (meets condition)
    log.debug("Inserting row that SHOULD notify")
    await conn.execute(
        "INSERT INTO chat_events(kind, text, priority) VALUES($1, $2, $3) RETURNING id, kind, text, priority;",
        "message", "hola", 7
    )

    # Wait for adapter to pick it up and event to run
    await asyncio.sleep(0.6)

    await conn.close()
    log.debug("PG connection closed")

    # --- Teardown app
    await adapter.stop()
    await mgr.stop()
    log.debug("Adapter and EventManager stopped")

    # Payload received by handler (single row matching condition)
    log.debug("Asserting payload", extra={"seen": seen})
    assert len(seen) == 1
    payload = seen[0]
    assert isinstance(payload, dict)
    assert payload["kind"] == "message"
    assert payload["text"] == "hola"
    assert int(payload["priority"]) == 7

    # ---- Metrics asserts ----
    snap = metrics.snapshot()

    def _get(name):
        return [c for c in snap["counters"] if c["name"] == name and c["labels"].get("event_id") == ev.id.value]

    enq = _get("jobs_enqueued_total")
    started = _get("jobs_started_total")
    succ = _get("jobs_succeeded_total")
    failed = _get("jobs_failed_total")

    log.debug("Metrics snapshot", extra={"enq": enq, "started": started, "succ": succ, "failed": failed})

    assert enq and enq[0]["value"] >= 1, "Expected at least one enqueued job from NOTIFY->adapter"
    assert started and started[0]["value"] >= 1, "Expected the job to start"
    assert succ and succ[0]["value"] >= 1, "Expected the job to succeed"
    assert not failed or failed[0]["value"] == 0, "Should not fail for happy path"
