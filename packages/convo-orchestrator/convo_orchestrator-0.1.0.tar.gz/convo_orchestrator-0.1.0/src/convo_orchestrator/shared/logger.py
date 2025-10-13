#shared/logger.py
"""
Ultra-lightweight, singleton log bus with topic support.

This module exposes a single global logging bus (LogBus) that
configures the Python logging root once (using Config) and lets you
publish log records to different "topics" without spawning multiple
logger instances.

Key properties:
- Singleton: only one LogBus exists.
- Topics: pass `topic="auth"`, `topic="billing"`, etc. It is injected
  as structured field (extra["topic"]) for downstream filtering.
- Zero-cost when disabled: uses isEnabledFor + lazy callables.
- Config-driven (via shared.Config): reads LOG_LEVEL and LOG_JSON once.

Environment:
    LOG_LEVEL = DEBUG|INFO|WARNING|ERROR|CRITICAL   (default: INFO)
    LOG_JSON  = true|false                          (default: false)
"""

from __future__ import annotations

import os
import inspect
import json
import logging
import threading
from typing import Any, Dict, Optional, Callable

from . import Config
def _resolve_level_name() -> str:
    cfg = Config.instance()
    return str(cfg.get("LOG_LEVEL", expected_type=str, default="INFO").unwrap_or("INFO")).upper()

def _resolve_json_mode() -> bool:
    cfg = Config.instance()
    return bool(cfg.get("LOG_JSON", expected_type=bool, default=True).unwrap_or(True))

def _resolve_force_mode() -> bool:
    cfg = Config.instance()
    return bool(cfg.get("LOG_FORCE", expected_type=bool, default=True).unwrap_or(True))

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "topic": getattr(record, "topic", None),
            "file": record.filename,
            "line": record.lineno,
            "func": record.funcName,
            "module": record.module,
            "process": record.process,
            "thread": record.thread,
        }
        # añade extras seguros
        for k, v in record.__dict__.items():
            if k in ("args","msg","topic","name","levelname","levelno","pathname",
                     "filename","module","exc_info","exc_text","stack_info","lineno",
                     "funcName","created","msecs","relativeCreated","thread","threadName",
                     "processName","process"):
                continue
            if k not in payload:
                try:
                    json.dumps({k: v})
                    payload[k] = v
                except Exception:
                    payload[k] = str(v)
        return json.dumps(payload, separators=(",", ":"))
    
def _ensure_configured() -> logging.Logger:
    """
    Configure a dedicated 'app' logger with JSON (por defecto) y sin propagación.
    Deja el root tal cual para no pelear con pytest.
    """
    level_name = _resolve_level_name()
    level = getattr(logging, level_name, logging.INFO)
    json_mode = _resolve_json_mode()

    app_logger = logging.getLogger("app")
    # Forzar configuración idempotente
    for h in list(app_logger.handlers):
        app_logger.removeHandler(h)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    if json_mode:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d [%(topic)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))

    app_logger.setLevel(level)
    app_logger.addHandler(handler)
    app_logger.propagate = False  # ← EVITA que pytest re-formatee

    logging.captureWarnings(True)
    return app_logger

def _compute_stacklevel() -> int:
    """
    Walk the call stack and return the first frame outside this module,
    so filename/lineno reflect the real caller.
    """
    this = os.path.abspath(__file__)
    for idx, frame in enumerate(inspect.stack(), start=1):
        try:
            if os.path.abspath(frame.filename) != this:
                return idx
        except Exception:
            break
    return 2

class LogBus:
    """
    Singleton log bus that routes log records to the Python root logger.

    Publish logs to different topics without creating multiple logger
    instances. All calls accept either a plain string or a zero-arg
    callable for lazy evaluation.

    Example:
        log = LogBus.instance()
        log.info("auth", lambda: f"User {uid} logged in")
        log.error("payments", "Charge failed", extra={"order_id": oid})

    Methods:
        debug(topic, msg, *, extra=None)
        info(topic, msg, *, extra=None)
        warning(topic, msg, *, extra=None)
        error(topic, msg, *, extra=None, exc=None)
        critical(topic, msg, *, extra=None, exc=None)

    Also provides topic() -> TopicLogger for ergonomic per-topic proxies,
    which are lightweight views over the same singleton.
    """

    _instance: Optional["LogBus"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._logger = _ensure_configured()

    @classmethod
    def instance(cls) -> "LogBus":
        with cls._lock:
            if cls._instance is None:
                cls._instance = LogBus()
            return cls._instance

    # ------------- internal -------------

    def _emit(
        self,
        level: int,
        topic: str,
        msg: Any,
        *,
        extra: Optional[Dict[str, Any]] = None,
        exc: Optional[BaseException] = None,
        stacklevel: Optional[int] = None,
    ) -> None:
        if not self._logger.isEnabledFor(level):
            return

        if callable(msg):
            try:
                msg = msg()
            except Exception as ex:
                msg = f"<log message callable raised: {ex!r}>"

        merged_extra = {"topic": topic}
        if extra:
            merged_extra.update({k: v for k, v in extra.items() if k != "topic"})

        effective_stacklevel = stacklevel or _compute_stacklevel()

        if exc is not None:
            self._logger.log(level, msg, exc_info=exc, extra=merged_extra, stacklevel=effective_stacklevel)
        else:
            self._logger.log(level, msg, extra=merged_extra, stacklevel=effective_stacklevel)

    # ------------- public -------------

    def debug(self, topic: str, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._emit(logging.DEBUG, topic, msg, extra=extra, stacklevel=stacklevel)

    def info(self, topic: str, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._emit(logging.INFO, topic, msg, extra=extra, stacklevel=stacklevel)

    def warning(self, topic: str, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._emit(logging.WARNING, topic, msg, extra=extra, stacklevel=stacklevel)

    def error(self, topic: str, msg: Any, *, extra: Optional[Dict[str, Any]] = None, exc: Optional[BaseException] = None, stacklevel: Optional[int] = None) -> None:
        self._emit(logging.ERROR, topic, msg, extra=extra, exc=exc, stacklevel=stacklevel)

    def critical(self, topic: str, msg: Any, *, extra: Optional[Dict[str, Any]] = None, exc: Optional[BaseException] = None, stacklevel: Optional[int] = None) -> None:
        self._emit(logging.CRITICAL, topic, msg, extra=extra, exc=exc, stacklevel=stacklevel)

    # Ergonomic per-topic proxy
    def topic(self, topic: str) -> "TopicLogger":
        """
        Return a lightweight proxy bound to a topic. This does not create
        any additional logger instances; it's only a small view object.
        """
        return TopicLogger(self, topic)


class TopicLogger:
    """
    Lightweight per-topic view over the LogBus singleton.

    Example:
        log = LogBus.instance().topic("auth")
        log.info("user created")
        log.error(lambda: f"Bad credentials for {email}")
    """

    __slots__ = ("_bus", "_topic")

    def __init__(self, bus: LogBus, topic: str) -> None:
        self._bus = bus
        self._topic = topic

    def debug(self, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._bus.debug(self._topic, msg, extra=extra, stacklevel=stacklevel)

    def info(self, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._bus.info(self._topic, msg, extra=extra, stacklevel=stacklevel)

    def warning(self, msg: Any, *, extra: Optional[Dict[str, Any]] = None, stacklevel: Optional[int] = None) -> None:
        self._bus.warning(self._topic, msg, extra=extra, stacklevel=stacklevel)

    def error(self, msg: Any, *, extra: Optional[Dict[str, Any]] = None, exc: Optional[BaseException] = None, stacklevel: Optional[int] = None) -> None:
        self._bus.error(self._topic, msg, extra=extra, exc=exc, stacklevel=stacklevel)

    def critical(self, msg: Any, *, extra: Optional[Dict[str, Any]] = None, exc: Optional[BaseException] = None, stacklevel: Optional[int] = None) -> None:
        self._bus.critical(self._topic, msg, extra=extra, exc=exc, stacklevel=stacklevel)


# Public helper to obtain a per-topic proxy without exposing LogBus internals
def get_logger(topic: str) -> TopicLogger:
    """
    Convenience function returning a per-topic logger view over the
    singleton LogBus. This does NOT create new logger instances.
    """
    return LogBus.instance().topic(topic)
