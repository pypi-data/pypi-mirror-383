"""
In-memory adapters for the asynchronous event manager.

This module provides:
- InMemoryEventRepository: simple, fast, and test-friendly repository
  for Event/Trigger/Subscription lifecycle.
- InMemoryMetrics: minimal MetricsSink with counters and histograms.
- SystemClock / FakeClock: time providers.

It is intentionally small and dependency-free, ideal for demos, tests,
and local development.

Example:
    from datetime import datetime, timedelta, timezone
    import asyncio
    from convo_orchestrator.shared import get_logger
    from convo_orchestrator.domain.events import (
        Event, EventId, Trigger, TriggerId, TriggerKind, Policy
    )
    from convo_orchestrator.application.events import EventManager, HandlerRegistry
    from convo_orchestrator.adapters.memory_events import (
        InMemoryEventRepository, InMemoryMetrics, SystemClock
    )

    # 1) Create repository, metrics, clock, and handler registry
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    # 2) Register a handler (sync or async)
    def hello_handler(ctx):
        print(f"Hello from event {ctx.event_id.value}! payload={ctx.payload}")
        return "ok"

    registry.register("hello", hello_handler)

    # 3) Define an Event and a time-based Trigger (interval)
    ev = Event(
        id=EventId("ev-1"),
        name="hello-every-2s",
        handler_name="hello",
        policy=Policy(timeout_sec=5.0, max_retries=1, max_concurrency=1),
        active=True,
    )
    repo.save_event(ev)

    trig = Trigger(
        id=TriggerId("tr-1"),
        kind=TriggerKind.INTERVAL,
        interval=timedelta(seconds=2),
        active=True,
    )
    repo.attach_trigger(ev.id, trig)

    # 4) Create the EventManager façade and start background services
    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    mgr.start()

    async def main():
        # Manually emit a job (bypasses the scheduler)
        await mgr.emit(ev.id, payload={"msg": "manual"})
        await asyncio.sleep(5)  # let the interval trigger run a couple of times
        st = mgr.status(ev.id).unwrap()
        print("Queue depth:", st.queue_depth, "Running:", st.running)
        await mgr.stop()
        snap = metrics.snapshot()
        print("Metrics:", snap)

    asyncio.run(main())
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..shared import Result, Option, AppError, ErrorKind, LogBus
from ..domain.events import (
    Event, EventId, Trigger, TriggerId, SubscriptionId, EventRepository, MetricsSink
)


# ---------------------------
# Clocks (adapters utility)
# ---------------------------

class SystemClock:
    """
    Real-time clock (UTC). Suitable for production use.

    Example:
        clk = SystemClock()
        now = clk.now()
    """
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FakeClock:
    """
    Fake, manually-advanced clock for deterministic tests.

    Example:
        clk = FakeClock()
        t0 = clk.now()           # fixed start
        clk.advance(seconds=10)  # move forward
        t1 = clk.now()
    """
    def __init__(self, start: Optional[datetime] = None) -> None:
        self._now = start or datetime(2024, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now

    def advance(self, *, seconds: float = 0, minutes: float = 0, hours: float = 0) -> None:
        from datetime import timedelta
        self._now = self._now + timedelta(seconds=seconds, minutes=minutes, hours=hours)


# ---------------------------
# In-memory Metrics
# ---------------------------

@dataclass
class _Histogram:
    buckets: List[float]
    counts: List[int]

class InMemoryMetrics(MetricsSink):
    """
    Minimal in-memory MetricsSink.

    - `inc(name, labels, value)` increments counters.
    - `observe(name, value, labels)` records histogram-like samples
      with simple fixed buckets per metric.

    Example:
        m = InMemoryMetrics()
        m.inc("jobs_started_total", {"event_id": "ev-1"})
        m.observe("job_duration_seconds", 0.35, {"event_id": "ev-1"})
        snap = m.snapshot()
    """

    def __init__(self) -> None:
        self._log = LogBus.instance().topic("events.metrics")
        self._lock = threading.Lock()
        self._counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], float] = defaultdict(float)
        self._hists: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], _Histogram] = {}

        # default buckets for durations (seconds)
        self._default_buckets = [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30]

    def _lbl_key(self, labels: Optional[Dict[str, str]]) -> Tuple[Tuple[str, str], ...]:
        if not labels:
            return tuple()
        return tuple(sorted(labels.items()))

    def inc(self, name: str, labels: Optional[Dict[str, str]] = None, value: float = 1.0) -> None:
        key = (name, self._lbl_key(labels))
        with self._lock:
            self._counters[key] += value

    def observe(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        key = (name, self._lbl_key(labels))
        with self._lock:
            hist = self._hists.get(key)
            if hist is None:
                hist = _Histogram(buckets=list(self._default_buckets), counts=[0] * (len(self._default_buckets) + 1))
                self._hists[key] = hist
            # find bucket
            idx = len(hist.buckets)
            for i, b in enumerate(hist.buckets):
                if value <= b:
                    idx = i
                    break
            hist.counts[idx] += 1

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable snapshot of counters and histograms.
        """
        with self._lock:
            counters = [
                {
                    "name": name,
                    "labels": dict(labels),
                    "value": val,
                }
                for (name, labels), val in self._counters.items()
            ]
            histograms = [
                {
                    "name": name,
                    "labels": dict(labels),
                    "buckets": hist.buckets,
                    "counts": hist.counts,
                }
                for (name, labels), hist in self._hists.items()
            ]
        return {"counters": counters, "histograms": histograms}


# ---------------------------
# In-memory Event Repository
# ---------------------------

class InMemoryEventRepository(EventRepository):
    """
    Simple in-memory repository for Events and Triggers.

    Relationships:
        - Events stored by EventId.
        - Triggers stored by TriggerId.
        - Subscriptions: mapping trigger_id -> set(event_id) and event_id -> set(trigger_id).

    This implementation is concurrency-safe for basic operations via a lock.

    Example:
        repo = InMemoryEventRepository()
        ev = Event(id=EventId("ev-1"), name="job", handler_name="h")
        repo.save_event(ev)
        trig = Trigger(id=TriggerId("tr-1"), kind=TriggerKind.INTERVAL, interval=timedelta(seconds=1))
        repo.attach_trigger(ev.id, trig)
        print(repo.list_events())
        print(repo.list_triggers(ev.id))
    """

    def __init__(self) -> None:
        self._log = LogBus.instance().topic("events.repo.mem")
        self._lock = threading.Lock()
        self._events: Dict[str, Event] = {}
        self._triggers: Dict[str, Trigger] = {}
        self._sub_by_trigger: Dict[str, set[str]] = defaultdict(set)
        self._sub_by_event: Dict[str, set[str]] = defaultdict(set)
        self._subs: Dict[str, Tuple[str, str]] = {}  # sub_id -> (trigger_id, event_id)
        self._sub_seq = 0

    # --- Event CRUD ---

    def get_event(self, event_id: EventId) -> Option[Event]:
        with self._lock:
            ev = self._events.get(event_id.value)
            return Option.Some(ev) if ev is not None else Option.None_()

    def list_events(self) -> List[Event]:
        with self._lock:
            return list(self._events.values())

    def save_event(self, event: Event) -> Result[None, AppError]:
        v = event.validate()
        if v.is_err():
            return Result.Err(v.unwrap_err())
        with self._lock:
            self._events[event.id.value] = event
        return Result.Ok(None)

    def remove_event(self, event_id: EventId) -> Result[None, AppError]:
        with self._lock:
            if event_id.value not in self._events:
                return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Event '{event_id.value}' not found"))
            # detach related subscriptions
            trig_ids = list(self._sub_by_event.get(event_id.value, set()))
            for tid in trig_ids:
                self._sub_by_event[event_id.value].discard(tid)
                self._sub_by_trigger[tid].discard(event_id.value)
            # drop empty keys
            self._sub_by_event.pop(event_id.value, None)
            # remove the event itself
            self._events.pop(event_id.value, None)
        return Result.Ok(None)

    # --- Triggers & Subscriptions ---

    def attach_trigger(self, event_id: EventId, trigger: Trigger) -> Result[SubscriptionId, AppError]:
        tv = trigger.validate()
        if tv.is_err():
            return Result.Err(tv.unwrap_err())

        with self._lock:
            if event_id.value not in self._events:
                return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Event '{event_id.value}' not found"))

            # upsert trigger
            self._triggers[trigger.id.value] = trigger

            # create a new subscription id
            self._sub_seq += 1
            sub_id = f"sub-{self._sub_seq}"
            self._subs[sub_id] = (trigger.id.value, event_id.value)

            self._sub_by_trigger[trigger.id.value].add(event_id.value)
            self._sub_by_event[event_id.value].add(trigger.id.value)

            return Result.Ok(SubscriptionId(sub_id))

    def detach_trigger(self, subscription_id: SubscriptionId) -> Result[None, AppError]:
        with self._lock:
            sub = self._subs.get(subscription_id.value)
            if not sub:
                return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Subscription '{subscription_id.value}' not found"))
            trig_id, ev_id = sub
            self._subs.pop(subscription_id.value, None)
            self._sub_by_trigger[trig_id].discard(ev_id)
            self._sub_by_event[ev_id].discard(trig_id)
            # do not remove trigger object; it may be linked to other events
        return Result.Ok(None)

    def list_triggers(self, event_id: Optional[EventId] = None) -> List[Trigger]:
        with self._lock:
            if event_id is None:
                return list(self._triggers.values())
            tids = self._sub_by_event.get(event_id.value, set())
            return [self._triggers[tid] for tid in tids if tid in self._triggers]

    # --- Helper API (not in port, but useful for adapters/testing) ---

    def events_for_trigger(self, trigger_id: TriggerId) -> List[Event]:
        """
        Return events linked to a trigger. Useful if a scheduler wants to
        enqueue only the relevant events rather than broadcasting.
        """
        with self._lock:
            ev_ids = self._sub_by_trigger.get(trigger_id.value, set())
            return [self._events[eid] for eid in ev_ids if eid in self._events]
