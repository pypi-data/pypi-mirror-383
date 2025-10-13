# How to Create an Event in `convo_orchestrator`

This guide explains step by step how to create, configure, and run an event
using the in-memory adapters of `convo_orchestrator`. Events can be triggered
manually, by time-based triggers, or by external adapters.

---

## 1. Import the required components

```python
from datetime import timedelta

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
)
```

---

## 2. Create the repository, metrics, clock, and handler registry

```python
repo = InMemoryEventRepository()
metrics = InMemoryMetrics()
clock = SystemClock()
registry = HandlerRegistry()
```

---

## 3. Define and register a handler

Handlers are just functions (sync or async) that receive an `EventContext`.

```python
def my_handler(ctx):
    print(f"Running handler for event={ctx.event_id.value}, payload={ctx.payload}")
    return "done"

registry.register("my-handler", my_handler)
```

---

## 4. Create an Event

An event defines the *what* and *how* to execute.

```python
ev = Event(
    id=EventId("ev-hello"),
    name="hello-event",
    handler_name="my-handler",
    policy=Policy(timeout_sec=2.0, max_retries=0, max_concurrency=1),
    active=True,
)
repo.save_event(ev)
```

---

## 5. (Optional) Attach a Trigger

Triggers define *when* to execute the event.

### Interval trigger example:

```python
trig = Trigger(
    id=TriggerId("tr-hello"),
    kind=TriggerKind.INTERVAL,
    interval=timedelta(seconds=10),
    active=True,
)
repo.attach_trigger(ev.id, trig)
```

This means the event will run every 10 seconds.

---

## 6. Create and start the EventManager

```python
mgr = EventManager(repo=repo, handler_registry=registry, clock=clock, metrics=metrics, scheduler_tick_ms=100)
mgr.start()
```

---

## 7. Manually emit an event (alternative to triggers)

```python
import asyncio

async def run():
    await mgr.emit(ev.id, payload={"msg": "manual trigger"})
    await asyncio.sleep(0.5)
    await mgr.stop()

asyncio.run(run())
```

---

## 8. Check event status and metrics

```python
status = mgr.status(ev.id).unwrap()
print("Last outcome:", status.last_outcome)

print("Metrics snapshot:", metrics.snapshot())
```

---

## Summary

1. Create infra (`repo`, `metrics`, `clock`, `registry`).
2. Define and register a handler.
3. Create an `Event` and save it.
4. Optionally attach a `Trigger` (e.g., INTERVAL, AT).
5. Start the `EventManager`.
6. Use `.emit()` for manual runs, or let triggers schedule runs.
7. Inspect `.status()` and metrics to monitor executions.

This workflow lets you compose flexible event-driven behaviors in
`convo_orchestrator`.
