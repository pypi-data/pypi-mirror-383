# adapters/postgres_notify.py

"""
PostgreSQL LISTEN/NOTIFY adapter that bridges database notifications
to domain EXTERNAL triggers.

Design:
- Subscribes to a set of channels and forwards notifications to the
  EventManager as events associated with EXTERNAL triggers where the
  TriggerId.value equals the channel name.
- Optionally derives the active channel set from the EventRepository
  (unless explicit channels are provided).
- Periodically refreshes the channel subscriptions to reflect repository changes.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Optional, Dict, List, Tuple

import asyncpg

from ..shared import AppError, ErrorKind, LogBus
from ..domain.events import TriggerId, TriggerKind, EventRepository
from ..application.events import EventManager


class PostgresNotifyAdapter:
    """
    Binds PostgreSQL NOTIFY to EXTERNAL triggers (TriggerId.value == channel).

    Lifecycle:
        - start(): Connect, LISTEN requested channels, spawn the listen loop.
        - stop():  Cancel the loop, UNLISTEN, and close the connection.

    Notes:
        - If channels are not provided, they are derived from active EXTERNAL triggers.
        - The adapter polls for changes in the set of desired channels at a fixed interval
          (`refresh_sec`) and updates LISTEN/UNLISTEN accordingly.
    """

    def __init__(
        self,
        *,
        manager: EventManager,
        repo: EventRepository,
        channels: Optional[List[str]] = None,
        log_topic: str = "events.pg",
        refresh_sec: float = 5.0,
    ) -> None:
        self._mgr = manager
        self._repo = repo
        self._log = LogBus.instance().topic(log_topic)
        self._refresh_sec = refresh_sec
        self._channels_override = channels
        self._conn: Optional[asyncpg.Connection] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._queue: asyncio.Queue[Tuple[int, str, Optional[str]]] = asyncio.Queue()
        self._listeners: set[str] = set()

    # --- Connection / channel resolution -------------------------------------

    def _dsn_from_env(self) -> Dict[str, Any]:
        """
        Build a DSN from standard PG* environment variables with safe defaults.
        """
        host = os.getenv("PGHOST", "localhost")
        port = int(os.getenv("PGPORT", "5432"))
        user = os.getenv("PGUSER", "postgres")
        password = os.getenv("PGPASSWORD", "")
        database = os.getenv("PGDATABASE", "postgres")
        return {"host": host, "port": port, "user": user, "password": password, "database": database}

    def _derive_channels(self) -> List[str]:
        """
        Determine which channels to LISTEN to.

        Priority:
            1) If explicit channels were provided at initialization, use them.
            2) Otherwise, inspect the repository for active EXTERNAL triggers.
        """
        if self._channels_override:
            return list(dict.fromkeys(self._channels_override))

        chans: List[str] = []
        for trig in self._repo.list_triggers():
            if trig.kind == TriggerKind.EXTERNAL and trig.active:
                chans.append(trig.id.value)
        return list(dict.fromkeys(chans))

    # --- Lifecycle ------------------------------------------------------------

    async def start(self) -> None:
        """
        Connect to PostgreSQL, LISTEN desired channels, and start the event loop.
        """
        if self._running:
            return
        cfg = self._dsn_from_env()
        self._conn = await asyncpg.connect(**cfg)

        for ch in self._derive_channels():
            await self._conn.execute(f'LISTEN "{ch}";')
            await self._conn.add_listener(ch, self._on_notify)
            self._listeners.add(ch)

        self._running = True
        self._task = asyncio.create_task(self._loop(), name="pg-listen-loop")

    async def stop(self) -> None:
        """
        Stop the event loop, UNLISTEN from all channels, and close the connection.
        """
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._conn:
            for ch in list(self._listeners):
                try:
                    await self._conn.remove_listener(ch, self._on_notify)
                except Exception:
                    # Best-effort cleanup.
                    pass
            self._listeners.clear()
            await self._conn.close()
            self._conn = None

    # --- Channel maintenance --------------------------------------------------

    async def _refresh_channels_if_needed(self) -> None:
        """
        Refresh LISTEN/UNLISTEN subscriptions if derived channels changed.
        """
        if self._channels_override or not self._conn:
            return

        desired = set(self._derive_channels())
        current = set(self._listeners)

        # Newly desired channels
        for ch in desired - current:
            await self._conn.execute(f'LISTEN "{ch}";')
            await self._conn.add_listener(ch, self._on_notify)
            self._listeners.add(ch)
            self._log.debug(lambda: f"LISTEN {ch}")

        # Channels no longer desired
        for ch in current - desired:
            await self._conn.execute(f'UNLISTEN "{ch}";')
            try:
                await self._conn.remove_listener(ch, self._on_notify)
            except Exception:
                # Best-effort cleanup.
                pass
            self._listeners.discard(ch)
            self._log.debug(lambda: f"UNLISTEN {ch}")

    # --- Notification processing ---------------------------------------------

    def _parse_payload(self, raw: Optional[str]) -> Any:
        """
        Try to JSON-decode the payload; fall back to raw string, or None.
        """
        if not raw:
            return None
        s = raw.strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            return s

    async def _emit_for_channel(self, channel: str, payload: Any, *, correlation_id: Optional[str]) -> None:
        """
        Resolve which events are associated with a channel and emit them.

        Strategy:
            - Prefer repository method `events_for_trigger(TriggerId)` if available.
            - Otherwise, iterate `list_events()` and check triggers per event.
        """
        evs = []
        if hasattr(self._repo, "events_for_trigger"):
            try:
                evs = self._repo.events_for_trigger(TriggerId(channel))  # type: ignore[attr-defined]
            except Exception:
                evs = []

        if not evs:
            for ev in self._repo.list_events():
                trigs = self._repo.list_triggers(ev.id)
                if any(t.id.value == channel for t in trigs):
                    evs.append(ev)

        for ev in evs:
            await self._mgr.emit(ev.id, payload=payload, correlation_id=correlation_id)

    def _on_notify(self, connection, pid: int, channel: str, payload: Optional[str]) -> None:
        """
        Listener callback registered with asyncpg; enqueues the notification.
        """
        try:
            self._queue.put_nowait((pid, channel, payload))
        except Exception:
            # Drop if queue is full or during shutdown.
            pass

    async def _loop(self) -> None:
        """
        Main loop: drain notifications and periodically refresh channel subscriptions.
        """
        while True:
            try:
                pid, channel, raw = await asyncio.wait_for(self._queue.get(), timeout=self._refresh_sec)
                payload = self._parse_payload(raw)
                self._log.debug(lambda: f"PG NOTIFY channel={channel} payload={payload!r}")
                await self._emit_for_channel(channel, payload, correlation_id=str(pid))
            except asyncio.TimeoutError:
                await self._refresh_channels_if_needed()
            except asyncio.CancelledError:
                break
            except Exception as ex:
                # Log and keep the loop alive.
                self._log.error("pg-listen-loop error", exc=ex)
                await asyncio.sleep(0.2)
