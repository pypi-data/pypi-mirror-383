#application/events.py
"""
Application layer for the asynchronous event manager.

This module provides a minimal but professional façade (`EventManager`)
plus a scheduler and a dispatcher. It orchestrates domain entities and
ports while remaining framework-agnostic.

Key goals:
- Small code surface and easy-to-follow flow.
- Fully asynchronous execution with asyncio.
- Transparent support for sync or async handlers.
- Policies: timeout, retries (with backoff hints), max_concurrency.
- Time-based triggers (AT, INTERVAL) scheduled in-application.
- CRUD by id, emit/manual run, status/metrics access.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Dict, Optional

from ..shared import Result, Option, AppError, ErrorKind, LogBus
from ..domain.events import (
    Event, EventId, Trigger, TriggerId, SubscriptionId,
    TriggerKind, Policy, JobOutcome, JobStatus, EventRepository,
    MetricsSink, Clock, EventContext, validate_new_subscription,
    BackoffKind
)


# ---------------------------
# Handler registry
# ---------------------------

class HandlerRegistry:
    """
    Simple registry that maps handler_name -> callable.
    Does not resolve/import modules by itself; adapters can populate it.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[EventContext], Any | Awaitable[Any]]] = {}

    def register(self, name: str, handler: Callable[[EventContext], Any | Awaitable[Any]]) -> None:
        self._handlers[name] = handler

    def get(self, name: str) -> Option[Callable[[EventContext], Any | Awaitable[Any]]]:
        return Option.Some(self._handlers[name]) if name in self._handlers else Option.None_()


# ---------------------------
# Runtime status snapshot
# ---------------------------

@dataclass
class EventRuntimeStatus:
    """
    Lightweight runtime status for ops-friendly visibility.
    """
    active: bool
    queue_depth: int
    running: int
    last_outcome: Optional[JobOutcome]
    next_run: Optional[datetime]


# ---------------------------
# Dispatcher
# ---------------------------

class DispatcherService:
    """
    Executes event handlers with respect to policies:
    - Detects sync vs async handlers.
    - Enforces timeout, retries (strategy hinted by Policy.backoff),
      and max_concurrency using an asyncio.Semaphore per Event.
    """

    def __init__(
        self,
        handler_registry: HandlerRegistry,
        metrics: Optional[MetricsSink] = None,
        log_topic: str = "events.dispatcher",
    ) -> None:
        self._handlers = handler_registry
        self._metrics = metrics
        self._log = LogBus.instance().topic(log_topic)
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._running: Dict[str, int] = {}

    def _sem_for(self, event: Event) -> asyncio.Semaphore:
        sem = self._semaphores.get(event.id.value)
        if sem is None or sem._value != event.policy.max_concurrency:
            sem = asyncio.Semaphore(event.policy.max_concurrency)
            self._semaphores[event.id.value] = sem
        return sem

    def running_count(self, event_id: EventId) -> int:
        return self._running.get(event_id.value, 0)

    async def _call_handler(self, handler: Callable[[EventContext], Any | Awaitable[Any]], ctx: EventContext) -> Any:
        if inspect.iscoroutinefunction(handler):
            return await handler(ctx)  # type: ignore[arg-type]
        # run sync handler in default executor to avoid blocking loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, handler, ctx)

    async def _sleep_backoff(self, attempt: int, policy: Policy) -> None:
        if attempt <= 0:
            return
        base = 0.5  # seconds default
        if policy.backoff == BackoffKind.FIXED:
            delay = base
        elif policy.backoff == BackoffKind.EXP:
            delay = base * (2 ** (attempt - 1))
        else:  # EXP_JITTER (simple jitter)
            import random
            delay = (base * (2 ** (attempt - 1))) * (0.5 + random.random() * 0.5)
        await asyncio.sleep(min(delay, 30.0))

    async def execute(self, event: Event, ctx: EventContext) -> JobOutcome:
        """
        Execute a single job respecting Policy. Returns a JobOutcome.
        """
        started = datetime.now(timezone.utc)
        last_err: Optional[AppError] = None
        handler_opt = self._handlers.get(event.handler_name)
        if handler_opt.is_none():
            err = AppError.handler_not_found(event.handler_name)
            return JobOutcome(JobStatus.ERR, started, datetime.now(timezone.utc), err, 0)

        handler = handler_opt.unwrap()
        sem = self._sem_for(event)

        # counters
        self._running[event.id.value] = self._running.get(event.id.value, 0) + 1
        if self._metrics:
            self._metrics.inc("jobs_started_total", {"event_id": event.id.value})

        try:
            for attempt in range(0, event.policy.max_retries + 1):
                try:
                    coro = self._call_handler(handler, ctx)
                    if event.policy.timeout_sec is not None:
                        async with sem:  # bounded concurrency
                            res = await asyncio.wait_for(coro, timeout=event.policy.timeout_sec)
                    else:
                        async with sem:
                            res = await coro

                    finished = datetime.now(timezone.utc)
                    if self._metrics:
                        self._metrics.inc("jobs_succeeded_total", {"event_id": event.id.value})
                        self._metrics.observe(
                            "job_duration_seconds",
                            (finished - started).total_seconds(),
                            {"event_id": event.id.value},
                        )
                    return JobOutcome(JobStatus.OK, started, finished, None, attempt, result_preview=_preview(res))
                except asyncio.CancelledError:
                    finished = datetime.now(timezone.utc)
                    if self._metrics:
                        self._metrics.inc("jobs_cancelled_total", {"event_id": event.id.value})
                    return JobOutcome(JobStatus.CANCELLED, started, finished, None, attempt)
                except asyncio.TimeoutError as ex:
                    finished = datetime.now(timezone.utc)
                    last_err = AppError.timeout(event.policy.timeout_sec)
                    self._log.warning(lambda: f"Job timeout event={event.id.value} after={event.policy.timeout_sec}s")
                    if self._metrics:
                        self._metrics.inc("jobs_failed_total", {"event_id": event.id.value})
                    return JobOutcome(JobStatus.ERR, started, finished, last_err, attempt)
                except Exception as ex:
                    # Convert to AppError (keep message)
                    last_err = ex if isinstance(ex, AppError) else AppError.handler_exec(ex)
                    self._log.warning(lambda: f"Job failed attempt={attempt} event={event.id.value} err={last_err}")
                    if attempt < event.policy.max_retries:
                        await self._sleep_backoff(attempt + 1, event.policy)
                        continue
                    finished = datetime.now(timezone.utc)
                    if self._metrics:
                        self._metrics.inc("jobs_failed_total", {"event_id": event.id.value})
                    return JobOutcome(JobStatus.ERR, started, finished, last_err, attempt)
        finally:
            self._running[event.id.value] = max(0, self._running.get(event.id.value, 1) - 1)


def _preview(value: Any, limit: int = 256) -> str:
    """
    Short string preview for ops: keeps responses small and safe to log.
    """
    try:
        s = str(value)
        return s if len(s) <= limit else s[:limit] + "…"
    except Exception:
        return "<unprintable>"


# ---------------------------
# Scheduler
# ---------------------------

class SchedulerService:
    """
    Time-based scheduler that computes next runs for AT and INTERVAL triggers.
    It enqueues jobs to the EventManager's queues (one per Event).
    """

    def __init__(
        self,
        repo: EventRepository,
        clock: Clock,
        queues: Dict[str, asyncio.Queue],
        log_topic: str = "events.scheduler",
        tick_ms: Optional[int] = None,
        metrics: Optional[MetricsSink] = None,
    ) -> None:
        self._repo = repo
        self._clock = clock
        self._queues = queues
        self._log = LogBus.instance().topic(log_topic)
        self._tick = (tick_ms / 1000.0) if tick_ms and tick_ms > 0 else 0.25
        self._task: Optional[asyncio.Task] = None
        self._next_run_overrides: Dict[str, datetime] = {}  # sub_id -> next run
        self._metrics = metrics
        self._consumed_at: set[str] = set()  # AT triggers already fired

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._loop(), name="event-scheduler-loop")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            now = self._clock.now()
            try:
                triggers = self._repo.list_triggers()
                for trig in triggers:
                    if not trig.active:
                        continue
                    if trig.kind not in (TriggerKind.AT, TriggerKind.INTERVAL):
                        continue  # external/condition handled by adapters
                    if trig.kind == TriggerKind.AT and trig.id.value in self._consumed_at:
                        continue  # one-shot already fired

                    # compute next run
                    key = trig.id.value
                    next_at = self._next_run_overrides.get(key)
                    if next_at is None:
                        nr = trig.next_run_after(now)
                        if nr.is_some():
                            next_at = nr.unwrap()
                            self._next_run_overrides[key] = next_at

                    if next_at and now >= next_at:
                        # Enqueue ONLY the events subscribed to this trigger.
                        # Prefer a repository reverse lookup if available; otherwise, fall back
                        # to filtering by list_triggers(event_id).
                        target_events = []
                        if hasattr(self._repo, "events_for_trigger"):
                            try:
                                target_events = self._repo.events_for_trigger(trig.id)  # type: ignore[attr-defined]
                            except Exception:
                                target_events = []
                        if not target_events:
                            # Fallback: derive targets by scanning event -> triggers
                            for ev in self._repo.list_events():
                                if not ev.active:
                                    continue
                                ev_trigs = self._repo.list_triggers(ev.id)
                                if any(t.id.value == trig.id.value for t in ev_trigs):
                                    target_events.append(ev)

                        for ev in target_events:
                            q = self._queues.get(ev.id.value)
                            if q:
                                await q.put({"trigger_id": trig.id.value, "payload": None})
                                # lightweight ops visibility
                                self._log.debug(lambda: f"Enqueued event={ev.id.value} by trigger={trig.id.value}")
                                # metrics: count scheduler enqueues
                                if self._metrics:
                                    self._metrics.inc("jobs_enqueued_total", {"event_id": ev.id.value})
                        # schedule next occurrence
                        if trig.kind == TriggerKind.INTERVAL and trig.interval:
                            self._next_run_overrides[key] = now + trig.interval
                        else:
                            # one-shot AT: remove override to avoid re-run
                            self._next_run_overrides.pop(key, None)
                            self._consumed_at.add(trig.id.value)

            except Exception as ex:
                self._log.error("Scheduler loop error", exc=ex)
            await asyncio.sleep(self._tick)


# ---------------------------
# Event Manager (façade)
# ---------------------------

class EventManager:
    """
    High-level façade to manage events:
    - CRUD: create, update, pause/resume, remove; attach/detach triggers.
    - Execution: emit (manual enqueue), test_run (immediate), start/stop runtime.
    - Monitoring: status snapshot and simple metrics counters (via MetricsSink).

    It maintains a per-event asyncio.Queue and a dispatcher loop consuming jobs.
    """

    def __init__(
        self,
        repo: EventRepository,
        handler_registry: HandlerRegistry,
        clock: Clock,
        metrics: Optional[MetricsSink] = None,
        log_topic: str = "events.manager",
        queue_maxsize: Optional[int] = None,
        scheduler_tick_ms: Optional[int] = None,
    ) -> None:
        self._repo = repo
        self._handlers = handler_registry
        self._clock = clock
        self._metrics = metrics
        self._log = LogBus.instance().topic(log_topic)
        self._queues: Dict[str, asyncio.Queue] = {}
        self._dispatcher = DispatcherService(handler_registry, metrics)
        self._scheduler = SchedulerService(repo, clock, self._queues, tick_ms=scheduler_tick_ms, metrics=metrics)
        self._queue_maxsize = queue_maxsize or 0  # 0 = unbounded
        self._consumer_task: Optional[asyncio.Task] = None
        self._per_event_consumers: dict[str, asyncio.Task] = {}
        self._last_outcome: Dict[str, JobOutcome] = {}

    # ---- lifecycle -------------------------------------------------

    def start(self) -> None:
        """
        Start background components (scheduler + consumer).
        """
        self._ensure_queues()
        self._scheduler.start()
        # spawn one lightweight consumer per event queue
        for ev in self._repo.list_events():
            eid = ev.id.value
            if eid not in self._per_event_consumers:
                q = self._queues.setdefault(eid, asyncio.Queue(self._queue_maxsize))
                self._per_event_consumers[eid] = asyncio.create_task(
                    self._consume_queue(eid, q),
                    name=f"event-consumer-{eid}",
                )

    async def stop(self) -> None:
        """
        Stop background components gracefully.
        """
        await self._scheduler.stop()
        # cancel per-event consumers
        for t in self._per_event_consumers.values():
            t.cancel()
        for t in self._per_event_consumers.values():
            try:
                await t
            except asyncio.CancelledError:
                pass
        self._per_event_consumers.clear()
        self._consumer_task = None

    # ---- CRUD ------------------------------------------------------

    def create_event(self, event: Event) -> Result[EventId, AppError]:
        """
        Validate and persist an event. Initializes its queue.
        """
        v = event.validate()
        if v.is_err():
            return Result.Err(v.unwrap_err())
        res = self._repo.save_event(event)
        if res.is_err():
            return Result.Err(res.unwrap_err())
        self._queues.setdefault(event.id.value, asyncio.Queue(self._queue_maxsize))
        return Result.Ok(event.id)

    def update_event(self, event: Event) -> Result[None, AppError]:
        """
        Replace an existing event definition (by id).
        """
        v = event.validate()
        if v.is_err():
            return Result.Err(v.unwrap_err())
        res = self._repo.save_event(event)
        if res.is_err():
            return Result.Err(res.unwrap_err())
        self._queues.setdefault(event.id.value, asyncio.Queue(self._queue_maxsize))
        return Result.Ok(None)

    def remove_event(self, event_id: EventId) -> Result[None, AppError]:
        res = self._repo.remove_event(event_id)
        if res.is_err():
            return Result.Err(res.unwrap_err())
        self._queues.pop(event_id.value, None)
        self._last_outcome.pop(event_id.value, None)
        return Result.Ok(None)

    def attach_trigger(self, event: Event, trigger: Trigger) -> Result[SubscriptionId, AppError]:
        """
        Validate and link a trigger to an event.
        """
        val = validate_new_subscription(event, trigger)
        if val.is_err():
            return Result.Err(val.unwrap_err())
        return self._repo.attach_trigger(event.id, trigger)

    def detach_trigger(self, subscription_id: SubscriptionId) -> Result[None, AppError]:
        return self._repo.detach_trigger(subscription_id)

    # ---- Execution -------------------------------------------------

    async def emit(self, event_id: EventId, *, payload: Any = None, correlation_id: Optional[str] = None) -> Result[None, AppError]:
        """
        Manually enqueue a job for the given event.
        """
        q = self._queues.get(event_id.value)
        if not q:
            return Result.Err(AppError.queue_unavailable(event_id.value))
        await q.put({"trigger_id": None, "payload": payload, "correlation_id": correlation_id})
        if self._metrics:
            self._metrics.inc("jobs_enqueued_total", {"event_id": event_id.value})
        return Result.Ok(None)

    async def test_run(self, event_id: EventId, *, payload: Any = None) -> Result[JobOutcome, AppError]:
        """
        Execute immediately in the current task (bypasses queue/scheduler).
        Useful for diagnostics.
        """
        ev_opt = self._repo.get_event(event_id)
        if ev_opt.is_none():
            return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Event '{event_id.value}' not found"))
        ev = ev_opt.unwrap()
        ctx = EventContext(event_id=ev.id, trigger_id=None, job_id=_job_id(), payload=payload)
        outcome = await self._dispatcher.execute(ev, ctx)
        self._last_outcome[ev.id.value] = outcome
        return Result.Ok(outcome)

    # ---- Monitoring ------------------------------------------------

    def status(self, event_id: EventId) -> Result[EventRuntimeStatus, AppError]:
        """
        Return a small status snapshot for an event.
        """
        ev_opt = self._repo.get_event(event_id)
        if ev_opt.is_none():
            return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Event '{event_id.value}' not found"))
        ev = ev_opt.unwrap()
        q = self._queues.get(event_id.value)
        last = self._last_outcome.get(event_id.value)
        # next_run estimation is left blank here; the scheduler computes per-trigger times.
        st = EventRuntimeStatus(
            active=ev.active,
            queue_depth=(q.qsize() if q else 0),
            running=self._dispatcher.running_count(event_id),
            last_outcome=last,
            next_run=None,
        )
        return Result.Ok(st)

    # ---- internals -------------------------------------------------

    def _ensure_queues(self) -> None:
        for ev in self._repo.list_events():
            self._queues.setdefault(ev.id.value, asyncio.Queue(self._queue_maxsize))

    async def _consume_queue(self, event_id_value: str, q: asyncio.Queue) -> None:
        """
        Dedicated consumer for a single event queue. Ensures items from this
        queue are dispatched ONLY to the corresponding event.
        """
        while True:
            item = await q.get()
            ev_opt = self._repo.get_event(EventId(event_id_value))
            if ev_opt.is_none():
                # event removed meanwhile; drop item gracefully
                continue
            ev = ev_opt.unwrap()
            ctx = EventContext(
                event_id=ev.id,
                trigger_id=TriggerId(item["trigger_id"]) if item.get("trigger_id") else None,
                job_id=_job_id(),
                payload=item.get("payload"),
                correlation_id=item.get("correlation_id"),
            )
            outcome = await self._dispatcher.execute(ev, ctx)
            self._last_outcome[ev.id.value] = outcome

# ---------------------------
# Helpers
# ---------------------------

def _job_id() -> str:
    """
    Cheap monotonic-based job id (not cryptographically unique).
    """
    return f"job-{int(time.monotonic_ns())}"
