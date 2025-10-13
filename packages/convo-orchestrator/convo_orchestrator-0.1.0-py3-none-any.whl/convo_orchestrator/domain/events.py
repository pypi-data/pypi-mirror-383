#domain/events.py
"""
Domain model for the asynchronous event manager.

This module defines the core, framework-agnostic concepts:
- Event identifiers and minimal metadata.
- Trigger types (At, Interval, External) and next-run calculation
  for time-based scheduling.
- Execution Policy (timeout, retries, backoff, concurrency caps).
- Event aggregate and validation rules.
- Job outcome and a small EventContext passed to handlers.
- Lightweight ports (interfaces) for scheduling/dispatch boundaries.

No infrastructure concerns here. No imports from frameworks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, Protocol, Union

from ..shared import AppError, ErrorKind, Result, Option


# ---------------------------
# Identifiers and primitives
# ---------------------------

@dataclass(frozen=True)
class EventId:
    """
    Strongly-typed identifier for an Event aggregate.
    """
    value: str


@dataclass(frozen=True)
class TriggerId:
    """
    Strongly-typed identifier for a Trigger definition.
    """
    value: str


@dataclass(frozen=True)
class SubscriptionId:
    """
    Identifier that links a Trigger to an Event.
    """
    value: str


# ---------------------------
# Handler types and context
# ---------------------------

@dataclass(frozen=True)
class EventContext:
    """
    Immutable context passed to handlers at invocation time.

    Attributes:
        event_id: The event being executed.
        trigger_id: The trigger that caused the execution (if any).
        job_id: An invocation identifier (assigned by the dispatcher).
        payload: Optional structured payload provided by the trigger/emit.
        correlation_id: For end-to-end trace correlation across systems.
        ts: Timestamp of enqueue or execution start (UTC).
    """
    event_id: EventId
    trigger_id: Optional[TriggerId]
    job_id: str
    payload: Any = None
    correlation_id: Optional[str] = None
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# A handler can be sync -> Any, or async -> Awaitable[Any]
SyncHandler = Callable[[EventContext], Any]
AsyncHandler = Callable[[EventContext], Awaitable[Any]]
Handler = Union[SyncHandler, AsyncHandler]


# ---------------------------
# Triggers
# ---------------------------

class TriggerKind(str, Enum):
    """
    Supported trigger kinds in the domain.
    """
    AT = "at"                  # one-shot at a fixed absolute time
    INTERVAL = "interval"      # periodic with a fixed delta
    EXTERNAL = "external"      # driven by adapters (DB polling, MQ, webhooks, etc.)
    CONDITION = "condition"    # boolean predicate evaluated externally


@dataclass(frozen=True)
class Trigger:
    """
    Trigger definition. For time-based triggers, the domain can compute
    the next run. EXTERNAL/CONDITION are coordinated by adapters.
    """
    id: TriggerId
    kind: TriggerKind
    at: Optional[datetime] = None
    interval: Optional[timedelta] = None
    jitter: Optional[timedelta] = None  # applied by scheduler/adapter, not here
    active: bool = True

    def validate(self) -> Result[None, AppError]:
        """
        Validate trigger attributes for its kind.
        """
        if not self.active:
            return Result.Ok(None)

        if self.kind == TriggerKind.AT:
            if self.at is None:
                return Result.Err(AppError(ErrorKind.VALIDATION, "AT trigger requires 'at' datetime"))
            # allow past 'at' — scheduler can choose to skip or run immediately

        elif self.kind == TriggerKind.INTERVAL:
            if self.interval is None or self.interval.total_seconds() <= 0:
                return Result.Err(AppError(ErrorKind.VALIDATION, "INTERVAL trigger requires positive 'interval'"))
        # EXTERNAL/CONDITION have no intrinsic constraints here
        return Result.Ok(None)

    def next_run_after(self, after: datetime) -> Option[datetime]:
        """
        Compute the next run instant for time-based triggers relative to 'after'.
        Returns Option.Some(datetime) for AT/INTERVAL, or Option.None_() for
        EXTERNAL/CONDITION (delegated to adapters).

        Assumes timezone-aware UTC datetimes.
        """
        if not self.active:
            return Option.None_()

        if self.kind == TriggerKind.AT:
            if self.at is None:
                return Option.None_()
            # If 'at' is in the past relative to 'after', scheduler decides whether to run once or drop.
            return Option.Some(self.at)

        if self.kind == TriggerKind.INTERVAL:
            if self.interval is None or self.interval.total_seconds() <= 0:
                return Option.None_()
            # Align next run strictly after 'after'.
            # Compute the next multiple of interval since an epoch (here: at or registration is not stored; use 'after')
            delta = self.interval
            # Advance by one interval to be strictly in the future
            return Option.Some(after + delta)

        # EXTERNAL / CONDITION: domain does not compute time
        return Option.None_()


# ---------------------------
# Policies
# ---------------------------

class BackoffKind(str, Enum):
    """
    Retry backoff strategies. Exact calculation is done in adapters.
    """
    FIXED = "fixed"
    EXP = "exp"
    EXP_JITTER = "exp_jitter"


@dataclass(frozen=True)
class Policy:
    """
    Execution policy applied by the dispatcher.

    Attributes:
        timeout_sec: Maximum wall time per job (None means unlimited).
        max_retries: Number of retry attempts on failure (>= 0).
        backoff: Strategy for delays between retries.
        max_concurrency: Upper bound of concurrent jobs for this event.
        rate_limit_per_sec: Optional rate cap for steady-state throughput.
        idempotency_key_fn: Optional logical key resolver (e.g., from payload).
    """
    timeout_sec: Optional[float] = 30.0
    max_retries: int = 0
    backoff: BackoffKind = BackoffKind.FIXED
    max_concurrency: int = 1
    rate_limit_per_sec: Optional[float] = None
    idempotency_key_fn: Optional[str] = None  # name of a resolver to be provided by adapters


# ---------------------------
# Event aggregate
# ---------------------------

@dataclass(frozen=True)
class Event:
    """
    Event aggregate: a handler plus its execution policy and metadata.

    The domain only models shape and invariants. Handler storage is
    left to application/adapters; here we keep a logical name key.
    """
    id: EventId
    name: str
    handler_name: str  # indirection to the actual callable registered elsewhere
    policy: Policy = field(default_factory=Policy)
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Result[None, AppError]:
        """
        Validate basic invariants for Event.
        """
        if not self.name or not self.handler_name:
            return Result.Err(AppError(ErrorKind.VALIDATION, "Event requires 'name' and 'handler_name'"))
        if self.policy.max_concurrency <= 0:
            return Result.Err(AppError(ErrorKind.VALIDATION, "max_concurrency must be >= 1"))
        if self.policy.max_retries < 0:
            return Result.Err(AppError(ErrorKind.VALIDATION, "max_retries must be >= 0"))
        if self.policy.timeout_sec is not None and self.policy.timeout_sec <= 0:
            return Result.Err(AppError(ErrorKind.VALIDATION, "timeout_sec must be > 0 when provided"))
        return Result.Ok(None)


# ---------------------------
# Job outcome
# ---------------------------

class JobStatus(str, Enum):
    """
    Final outcome status for a handler invocation.
    """
    OK = "ok"
    ERR = "err"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class JobOutcome:
    """
    Result of a single event invocation.
    """
    status: JobStatus
    started_at: datetime
    finished_at: datetime
    error: Optional[AppError] = None
    retries: int = 0
    result_preview: Optional[str] = None  # adapters may store a short preview for ops UX


# ---------------------------
# Ports (interfaces)
# ---------------------------

class Clock(Protocol):
    """
    Clock abstraction for deterministic testing and scheduling.
    """
    def now(self) -> datetime: ...


class EventRepository(Protocol):
    """
    Persistence port for Event aggregates and their subscriptions.

    An in-memory adapter is perfectly fine for many cases; a DB-backed one
    can be plugged in without changing domain/application code.
    """
    def get_event(self, event_id: EventId) -> Option[Event]: ...
    def list_events(self) -> list[Event]: ...
    def save_event(self, event: Event) -> Result[None, AppError]: ...
    def remove_event(self, event_id: EventId) -> Result[None, AppError]: ...

    def attach_trigger(self, event_id: EventId, trigger: Trigger) -> Result[SubscriptionId, AppError]: ...
    def detach_trigger(self, subscription_id: SubscriptionId) -> Result[None, AppError]: ...
    def list_triggers(self, event_id: Optional[EventId] = None) -> list[Trigger]: ...


class MetricsSink(Protocol):
    """
    Observability port for counters and histograms. Optional.
    """
    def inc(self, name: str, labels: Optional[dict[str, str]] = None, value: float = 1.0) -> None: ...
    def observe(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None: ...


# ---------------------------
# Utilities
# ---------------------------

def validate_new_subscription(event: Event, trigger: Trigger) -> Result[None, AppError]:
    """
    Validate that an Event and Trigger can be linked.
    """
    ev = event.validate()
    if ev.is_err():
        return ev
    tv = trigger.validate()
    if tv.is_err():
        return tv
    if not event.active:
        return Result.Err(AppError.not_active("Event"))
    if not trigger.active:
        return Result.Err(AppError.not_active("Trigger"))
    return Result.Ok(None)
