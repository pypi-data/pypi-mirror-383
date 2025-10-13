
#shared/error.py
"""
Error definitions for the application.

This module provides a lightweight way to define and raise
domain-agnostic application errors. Errors are categorized by
`ErrorKind` and wrapped in `AppError`, which can be extended
as needed across the system.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional


class ErrorKind(str, Enum):
    """
    Enumeration of error categories used across the application.
    """

    # generic
    UNKNOWN = "UnknownError"
    VALIDATION = "ValidationError"
    CONFLICT = "ConflictError"
    NOT_FOUND = "NotFoundError"

    # events/dispatch
    HANDLER_NOT_FOUND = "HandlerNotFound"
    HANDLER_EXEC_ERROR = "HandlerExecutionError"
    TIMEOUT = "TimeoutError"
    CANCELLED = "CancelledError"
    NOT_ACTIVE = "NotActiveError"
    QUEUE_UNAVAILABLE = "QueueUnavailable"

    # infra/adapters
    REPOSITORY_ERROR = "RepositoryError"
    SCHEDULER_ERROR = "SchedulerError"


class AppError(Exception):
    """
    Base application error wrapper.

    Attributes:
        kind (ErrorKind): The category of the error.
        message (str): A human-readable description of the error.
        cause (Optional[BaseException]): Optional original exception.
    """

    def __init__(self, kind: ErrorKind = ErrorKind.UNKNOWN, message: str = "", *, cause: Optional[BaseException] = None):
        self.kind = kind
        self.message = message or kind.value
        self.cause = cause
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.kind}] {self.message}"

    # ---- convenience constructors ----
    @classmethod
    def handler_not_found(cls, name: str) -> "AppError":
        return cls(ErrorKind.HANDLER_NOT_FOUND, f"Handler '{name}' not registered")

    @classmethod
    def handler_exec(cls, exc: BaseException) -> "AppError":
        return cls(ErrorKind.HANDLER_EXEC_ERROR, str(exc), cause=exc)

    @classmethod
    def timeout(cls, seconds: float | None = None) -> "AppError":
        msg = "Operation timed out" if seconds is None else f"Operation timed out after {seconds:.3f}s"
        return cls(ErrorKind.TIMEOUT, msg)

    @classmethod
    def queue_unavailable(cls, event_id: str) -> "AppError":
        return cls(ErrorKind.QUEUE_UNAVAILABLE, f"Event '{event_id}' has no initialized queue")

    @classmethod
    def not_active(cls, what: str) -> "AppError":
        return cls(ErrorKind.NOT_ACTIVE, f"{what} is inactive")

    @classmethod
    def repo(cls, msg: str) -> "AppError":
        return cls(ErrorKind.REPOSITORY_ERROR, msg)

    @classmethod
    def scheduler(cls, msg: str) -> "AppError":
        return cls(ErrorKind.SCHEDULER_ERROR, msg)
