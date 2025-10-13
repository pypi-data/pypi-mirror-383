"""
Root package for the backend application.

This package follows a hexagonal (ports & adapters) architecture,
separating concerns between the core domain logic, application
use cases, infrastructure adapters, and shared utilities.
"""

# Shared layer
from .shared import (
    AppError,
    ErrorKind,
    Result,
    Option,
    Config,
    LogBus,
    TopicLogger,
    get_logger,
)

# Domain layer
from .domain.events import (
    Event,
    EventId,
    Trigger,
    TriggerId,
    SubscriptionId,
    TriggerKind,
    Policy,
    BackoffKind,
    JobOutcome,
    JobStatus,
    EventContext,
)

# Application layer
from .application.events import (
    EventManager,
    HandlerRegistry,
)

# Adapters (in-memory defaults)
from .adapters.memory_events import (
    InMemoryEventRepository,
    InMemoryMetrics,
    SystemClock,
    FakeClock,
)

from .adapters.postgres_notify import PostgresNotifyAdapter

__all__ = [
    # shared
    "AppError",
    "ErrorKind",
    "Result",
    "Option",
    "Config",
    "LogBus",
    "TopicLogger",
    "get_logger",

    # domain
    "Event",
    "EventId",
    "Trigger",
    "TriggerId",
    "SubscriptionId",
    "TriggerKind",
    "Policy",
    "BackoffKind",
    "JobOutcome",
    "JobStatus",
    "EventContext",

    # application
    "EventManager",
    "HandlerRegistry",

    # adapters
    "InMemoryEventRepository",
    "InMemoryMetrics",
    "SystemClock",
    "FakeClock",
]
