"""
Shared module.

This package contains reusable, framework-agnostic components,
such as error definitions, utility types (Result/Option), and
other helpers that can be safely imported from any layer.
"""

from .error import AppError, ErrorKind
from .result import Result, Option
from .config import Config
from .logger import LogBus, get_logger, TopicLogger

__all__ = [
    "AppError",
    "ErrorKind",
    "Result",
    "Option",
    "Config",
    "LogBus",
    "TopicLogger",
    "get_logger",
]
