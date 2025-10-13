"""
Integration tests for in-memory adapters of convo_orchestrator.

These tests exercise the EventManager façade with the in-memory
EventRepository, Metrics sink, and SystemClock. They validate:
- Event/Trigger CRUD through the repository.
- Time-based scheduling (INTERVAL, AT one-shot).
- Manual emit/queue handling.
- Sync and async handlers execution.
- Retry policy behavior.
- Basic metrics increments and snapshot exposure.
- Fan-in correctness (each queue item is dispatched to its event).
- Scheduler targeting only subscribed events (no broadcast).
"""

from __future__ import annotations

import asyncio
from datetime import timedelta, timezone, datetime

import pytest

from convo_orchestrator import (
    InMemoryEventRepository,
    InMemoryMetrics,
    SystemClock,
    EventManager,
    HandlerRegistry,
    Event,
    EventId,
    Trigger,
    TriggerId,
    TriggerKind,
    Policy,
    JobStatus,
)
from convo_orchestrator.shared import get_logger

log = get_logger("tests.events")


# --------------------------------------------------------------------------------------
# Original tests (tweaked minimally) + DEBUG logs
# --------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_interval_trigger_runs_handler_and_updates_status(tmp_path):
    """
    It should schedule an INTERVAL trigger and execute the handler
    at least once, updating status with last outcome.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    def handler_hello(ctx):
        print(f"[handler_hello] payload={ctx.payload} event={ctx.event_id.value}")
        return "ok-sync"

    registry.register("hello", handler_hello)

    ev = Event(
        id=EventId("ev-interval"),
        name="hello-interval",
        handler_name="hello",
        policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug(f"[interval] event saved: id={ev.id.value}, handler={ev.handler_name}")

    trig = Trigger(
        id=TriggerId("tr-interval"),
        kind=TriggerKind.INTERVAL,
        interval=timedelta(milliseconds=200),
        active=True,
    )
    assert repo.attach_trigger(ev.id, trig).is_ok()
    log.debug(f"[interval] trigger attached: trig={trig.id.value} kind={trig.kind} interval={trig.interval}")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics, scheduler_tick_ms=50)
    log.debug("[interval] starting manager")
    mgr.start()

    await asyncio.sleep(0.7)

    status_res = mgr.status(ev.id)
    assert status_res.is_ok()
    status = status_res.unwrap()
    log.debug(f"[interval] status: last_outcome={status.last_outcome} running={status.running} queue={status.queue_depth}")
    assert status.last_outcome is not None
    assert status.last_outcome.status in (JobStatus.OK, JobStatus.ERR)

    log.debug("[interval] stopping manager")
    await mgr.stop()

    snap = metrics.snapshot()
    started = [
        c for c in snap["counters"]
        if c["name"] == "jobs_started_total" and c["labels"].get("event_id") == ev.id.value
    ]
    log.debug(f"[interval] metrics started={started}")
    assert started and started[0]["value"] >= 1


@pytest.mark.asyncio
async def test_manual_emit_executes_with_payload_and_metrics():
    """
    It should enqueue a manual job via emit() and execute the handler,
    recording metrics and exposing the last outcome in status.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    def handler_payload(ctx):
        assert ctx.payload == {"k": 1}
        return "manual-ok"

    registry.register("with-payload", handler_payload)

    ev = Event(
        id=EventId("ev-manual"),
        name="manual",
        handler_name="with-payload",
        policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug(f"[manual] event saved: id={ev.id.value}")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    log.debug("[manual] starting manager")
    mgr.start()

    log.debug("[manual] emitting payload")
    assert (await mgr.emit(ev.id, payload={"k": 1})).is_ok()

    await asyncio.sleep(0.2)

    status = mgr.status(ev.id).unwrap()
    log.debug(f"[manual] status last_outcome={status.last_outcome}")
    assert status.last_outcome is not None
    assert status.last_outcome.status == JobStatus.OK
    assert status.last_outcome.result_preview is not None

    log.debug("[manual] stopping manager")
    await mgr.stop()

    snap = metrics.snapshot()
    succ = [
        c for c in snap["counters"]
        if c["name"] == "jobs_succeeded_total" and c["labels"].get("event_id") == ev.id.value
    ]
    log.debug(f"[manual] metrics succeeded={succ}")
    assert succ and succ[0]["value"] >= 1


@pytest.mark.asyncio
async def test_retry_policy_succeeds_after_one_failure():
    """
    Dispatcher should retry according to policy and eventually succeed.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    calls = {"n": 0}

    async def flaky(ctx):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("transient")
        return "ok-after-retry"

    registry.register("flaky", flaky)

    ev = Event(
        id=EventId("ev-retry"),
        name="flaky-event",
        handler_name="flaky",
        policy=Policy(timeout_sec=2.0, max_retries=1, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug(f"[retry] event saved: id={ev.id.value} policy={ev.policy}")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    log.debug("[retry] test_run starting")
    outcome_res = await mgr.test_run(ev.id)
    assert outcome_res.is_ok()
    outcome = outcome_res.unwrap()
    log.debug(f"[retry] outcome={outcome.status} retries={outcome.retries} calls={calls['n']}")

    assert outcome.status == JobStatus.OK
    assert outcome.retries == 1
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_sync_and_async_handlers_via_test_run():
    """
    test_run() executes immediately (no queue), supporting both sync and async handlers.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    def sync_handler(ctx):
        return f"sync:{ctx.event_id.value}"

    async def async_handler(ctx):
        await asyncio.sleep(0.01)
        return f"async:{ctx.event_id.value}"

    registry.register("sync", sync_handler)
    registry.register("async", async_handler)

    ev_sync = Event(
        id=EventId("ev-sync"),
        name="sync",
        handler_name="sync",
        policy=Policy(timeout_sec=1.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    ev_async = Event(
        id=EventId("ev-async"),
        name="async",
        handler_name="async",
        policy=Policy(timeout_sec=1.0, max_retries=0, max_concurrency=1),
        active=True,
    )

    assert repo.save_event(ev_sync).is_ok()
    assert repo.save_event(ev_async).is_ok()
    log.debug("[sync/async] events saved")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)

    log.debug("[sync/async] test_run sync")
    out1 = (await mgr.test_run(ev_sync.id)).unwrap()
    log.debug(f"[sync/async] sync outcome={out1.status} preview={out1.result_preview!r}")

    log.debug("[sync/async] test_run async")
    out2 = (await mgr.test_run(ev_async.id)).unwrap()
    log.debug(f"[sync/async] async outcome={out2.status} preview={out2.result_preview!r}")

    assert out1.status == JobStatus.OK
    assert out2.status == JobStatus.OK
    assert out1.result_preview.startswith("sync:")
    assert out2.result_preview.startswith("async:")


def test_attach_and_detach_trigger_in_repository():
    """
    InMemoryEventRepository should attach and detach triggers, reflecting changes in listings.
    """
    repo = InMemoryEventRepository()

    ev = Event(
        id=EventId("ev-crud"),
        name="crud",
        handler_name="noop",
        policy=Policy(),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug("[crud] event saved")

    trig = Trigger(
        id=TriggerId("tr-crud"),
        kind=TriggerKind.INTERVAL,
        interval=timedelta(seconds=1),
        active=True,
    )
    sub_res = repo.attach_trigger(ev.id, trig)
    assert sub_res.is_ok()
    sub_id = sub_res.unwrap()
    log.debug(f"[crud] trigger attached sub_id={sub_id.value}")

    listed = repo.list_triggers(ev.id)
    log.debug(f"[crud] triggers listed={ [t.id.value for t in listed] }")
    assert len(listed) == 1
    assert listed[0].id.value == "tr-crud"

    assert repo.detach_trigger(sub_id).is_ok()
    listed2 = repo.list_triggers(ev.id)
    log.debug(f"[crud] triggers after detach={ [t.id.value for t in listed2] }")
    assert len(listed2) == 0


@pytest.mark.asyncio
async def test_remove_event_cleans_up_repository_mappings():
    """
    Removing an event should clean up its trigger subscriptions.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    registry.register("noop", lambda ctx: None)

    ev = Event(
        id=EventId("ev-remove"),
        name="remove",
        handler_name="noop",
        policy=Policy(),
        active=True,
    )
    repo.save_event(ev)
    log.debug("[remove] event saved")

    trig = Trigger(
        id=TriggerId("tr-remove"),
        kind=TriggerKind.INTERVAL,
        interval=timedelta(seconds=1),
        active=True,
    )
    repo.attach_trigger(ev.id, trig)
    log.debug("[remove] trigger attached")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    log.debug("[remove] starting manager")
    mgr.start()
    await asyncio.sleep(0.05)

    assert repo.remove_event(ev.id).is_ok()
    log.debug("[remove] event removed from repository")

    await asyncio.sleep(0.05)
    log.debug("[remove] stopping manager")
    await mgr.stop()


# --------------------------------------------------------------------------------------
# NEW tests: multi-event isolation, scheduler targeting, and AT one-shot
# --------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_consumer_routes_items_to_correct_event_with_two_queues():
    """
    Ensure the consumer fan-in dispatches queue items to their correct events (no cross-dispatch).
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    seen = {"a": [], "b": []}

    def handler_a(ctx):
        seen["a"].append(ctx.payload)
        return "A!"

    def handler_b(ctx):
        seen["b"].append(ctx.payload)
        return "B!"

    registry.register("hA", handler_a)
    registry.register("hB", handler_b)

    ev_a = Event(id=EventId("ev-a"), name="A", handler_name="hA", policy=Policy(), active=True)
    ev_b = Event(id=EventId("ev-b"), name="B", handler_name="hB", policy=Policy(), active=True)
    assert repo.save_event(ev_a).is_ok()
    assert repo.save_event(ev_b).is_ok()
    log.debug("[fan-in] events saved: ev-a, ev-b")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    log.debug("[fan-in] starting manager")
    mgr.start()

    log.debug("[fan-in] emitting to A")
    await mgr.emit(ev_a.id, payload={"event": "a", "i": 1})
    log.debug("[fan-in] emitting to B")
    await mgr.emit(ev_b.id, payload={"event": "b", "i": 2})

    await asyncio.sleep(0.3)

    await mgr.stop()
    log.debug(f"[fan-in] seen: A={seen['a']} B={seen['b']}")

    assert seen["a"] == [{"event": "a", "i": 1}]
    assert seen["b"] == [{"event": "b", "i": 2}]


@pytest.mark.asyncio
async def test_scheduler_targets_only_subscribed_events_no_broadcast():
    """
    The scheduler should enqueue only events subscribed to a trigger, not broadcast to all.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    hits = {"a": 0, "b": 0}

    def handler_a(ctx):
        hits["a"] += 1
        return "ok-a"

    def handler_b(ctx):
        hits["b"] += 1
        return "ok-b"

    registry.register("hA", handler_a)
    registry.register("hB", handler_b)

    ev_a = Event(id=EventId("ev-a2"), name="A2", handler_name="hA", policy=Policy(), active=True)
    ev_b = Event(id=EventId("ev-b2"), name="B2", handler_name="hB", policy=Policy(), active=True)
    assert repo.save_event(ev_a).is_ok()
    assert repo.save_event(ev_b).is_ok()
    log.debug("[no-broadcast] events saved")

    trig = Trigger(
        id=TriggerId("tr-only-a"),
        kind=TriggerKind.INTERVAL,
        interval=timedelta(milliseconds=150),
        active=True,
    )
    assert repo.attach_trigger(ev_a.id, trig).is_ok()
    log.debug("[no-broadcast] trigger attached to A only")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics, scheduler_tick_ms=50)
    log.debug("[no-broadcast] starting manager")
    mgr.start()

    await asyncio.sleep(0.5)
    await mgr.stop()
    log.debug(f"[no-broadcast] hits={hits}")

    assert hits["a"] >= 1
    assert hits["b"] == 0


@pytest.mark.asyncio
async def test_at_trigger_runs_once_only():
    """
    AT trigger should fire exactly once (one-shot), not repeatedly.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    timestamps: list[datetime] = []

    def handler_once(ctx):
        timestamps.append(datetime.now(timezone.utc))
        return "once"

    registry.register("once", handler_once)

    ev = Event(
        id=EventId("ev-once"),
        name="once",
        handler_name="once",
        policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug("[AT] event saved")

    at_time = datetime.now(timezone.utc) + timedelta(milliseconds=200)
    trig = Trigger(
        id=TriggerId("tr-at"),
        kind=TriggerKind.AT,
        at=at_time,
        active=True,
    )
    assert repo.attach_trigger(ev.id, trig).is_ok()
    log.debug(f"[AT] trigger attached at={at_time.isoformat()}")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics, scheduler_tick_ms=50)
    log.debug("[AT] starting manager")
    mgr.start()

    await asyncio.sleep(0.5)
    await asyncio.sleep(0.5)

    await mgr.stop()
    log.debug(f"[AT] executions={len(timestamps)} times={timestamps}")

    assert len(timestamps) == 1, f"Expected exactly one execution, got {len(timestamps)}"


@pytest.mark.asyncio
async def test_timeout_produces_err_and_increments_failed_metric():
    """
    A handler that runs longer than policy.timeout_sec should end with JobStatus.ERR
    (current implementation treats asyncio.TimeoutError as a generic failure),
    and increment jobs_failed_total.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    async def slow(ctx):
        await asyncio.sleep(0.2)
        return "too-late"

    registry.register("slow", slow)

    ev = Event(
        id=EventId("ev-timeout"),
        name="timeout",
        handler_name="slow",
        policy=Policy(timeout_sec=0.05, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug(f"[timeout] event saved with timeout={ev.policy.timeout_sec}s")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)

    log.debug("[timeout] test_run starting")
    outcome = (await mgr.test_run(ev.id)).unwrap()
    log.debug(f"[timeout] outcome={outcome.status} retries={outcome.retries} err={outcome.error}")

    assert outcome.status == JobStatus.ERR

    snap = metrics.snapshot()
    failed = [
        c for c in snap["counters"]
        if c["name"] == "jobs_failed_total" and c["labels"].get("event_id") == ev.id.value
    ]
    log.debug(f"[timeout] metrics failed={failed}")
    assert failed and failed[0]["value"] >= 1


@pytest.mark.asyncio
async def test_per_event_serial_execution_second_job_waits_until_first_finishes():
    """
    With the current design (one consumer per event queue),
    jobs for the same event run serially. This test ensures the second job
    does not start until the first job completes.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    started = []
    finished = []
    gate = asyncio.Event()

    async def blocking(ctx):
        started.append(("start", ctx.payload))
        await gate.wait()
        finished.append(("end", ctx.payload))
        return "done"

    registry.register("block", blocking)

    ev = Event(
        id=EventId("ev-serial"),
        name="serial",
        handler_name="block",
        policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug("[serial] event saved")

    mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics)
    log.debug("[serial] starting manager")
    mgr.start()

    log.debug("[serial] emit #1")
    assert (await mgr.emit(ev.id, payload=1)).is_ok()
    log.debug("[serial] emit #2")
    assert (await mgr.emit(ev.id, payload=2)).is_ok()

    await asyncio.sleep(0.1)
    log.debug(f"[serial] started={started} finished={finished}")
    assert started == [("start", 1)]
    assert finished == []

    gate.set()
    await asyncio.sleep(0.2)
    await mgr.stop()
    log.debug(f"[serial] final started={started} finished={finished}")

    assert started == [("start", 1), ("start", 2)]
    assert finished == [("end", 1), ("end", 2)]


@pytest.mark.asyncio
async def test_condition_trigger_emits_when_predicate_true_without_adapter():
    """
    CONDITION triggers are not handled by the scheduler; typically an adapter/worker
    evaluates the predicate and emits jobs. This test simulates that worker inline:
    - We attach a CONDITION trigger to an event (for bookkeeping).
    - A lightweight in-test poller checks a predicate against in-memory state.
    - When predicate becomes True, it emits exactly once with a payload.
    - We assert handler execution and metrics increments.
    """
    repo = InMemoryEventRepository()
    metrics = InMemoryMetrics()
    clock = SystemClock()
    registry = HandlerRegistry()

    seen: list[dict] = []

    def handler(ctx):
        seen.append(ctx.payload)
        return "ok"

    registry.register("cond-h", handler)

    ev = Event(
        id=EventId("ev-cond"),
        name="conditioned",
        handler_name="cond-h",
        policy=Policy(timeout_sec=1.0, max_retries=0, max_concurrency=1),
        active=True,
    )
    assert repo.save_event(ev).is_ok()
    log.debug("[cond] event saved")

    trig = Trigger(
        id=TriggerId("tr-cond"),
        kind=TriggerKind.CONDITION,
        active=True,
    )
    assert repo.attach_trigger(ev.id, trig).is_ok()
    log.debug("[cond] condition trigger attached (for bookkeeping)")

    mgr = EventManager(
        repo=repo,
        handler_registry=registry,
        clock=clock,
        metrics=metrics,
        scheduler_tick_ms=50,
    )
    log.debug("[cond] starting manager")
    mgr.start()

    state = {"ready": False}

    def predicate() -> bool:
        return state["ready"]

    def payload_factory() -> dict:
        return {"source": "condition", "x": 42}

    async def flip_later():
        await asyncio.sleep(0.2)
        state["ready"] = True
        log.debug("[cond] predicate flipped to True")

    stop_ev = asyncio.Event()

    async def condition_poller():
        try:
            emitted = False
            deadline = asyncio.get_event_loop().time() + 1.5
            while asyncio.get_event_loop().time() < deadline:
                if predicate() and not emitted:
                    log.debug("[cond] predicate True -> emitting job")
                    res = await mgr.emit(ev.id, payload=payload_factory())
                    assert res.is_ok(), f"emit() failed: {res}"
                    emitted = True
                    break
                await asyncio.sleep(0.05)
        finally:
            stop_ev.set()

    flip_task = asyncio.create_task(flip_later())
    poller_task = asyncio.create_task(condition_poller())

    await asyncio.wait_for(stop_ev.wait(), timeout=2.0)
    await asyncio.sleep(0.2)

    poller_task.cancel()
    try:
        await poller_task
    except asyncio.CancelledError:
        pass
    flip_task.cancel()
    try:
        await flip_task
    except asyncio.CancelledError:
        pass

    await mgr.stop()
    log.debug(f"[cond] seen={seen}")

    assert seen == [{"source": "condition", "x": 42}], "Handler should receive the condition payload exactly once"

    snap = metrics.snapshot()

    def _get(name):
        return [
            c for c in snap["counters"]
            if c["name"] == name and c["labels"].get("event_id") == ev.id.value
        ]

    enq = _get("jobs_enqueued_total")
    started = _get("jobs_started_total")
    succ = _get("jobs_succeeded_total")
    failed = _get("jobs_failed_total")

    log.debug(f"[cond] metrics enq={enq} started={started} succ={succ} failed={failed}")

    assert enq and enq[0]["value"] >= 1, "Expected at least one enqueued job from the condition poller"
    assert started and started[0]["value"] >= 1, "Expected the job to start"
    assert succ and succ[0]["value"] >= 1, "Expected the job to succeed"
    assert not failed or failed[0]["value"] == 0, "No failures expected for happy path"
