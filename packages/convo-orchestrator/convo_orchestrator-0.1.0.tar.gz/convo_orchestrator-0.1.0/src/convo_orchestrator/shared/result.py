#shared/result.py
"""
Rust-inspired Result and Option types for Python.

This module provides functional-style types for safe error and
optional value handling. Inspired by Rust's `Result<T, E>` and
`Option<T>`, they encourage explicit handling of success,
failure, and absence of values.
"""

from typing import Generic, TypeVar, Union, Callable
from . import AppError

T = TypeVar("T")
E = TypeVar("E", bound=AppError)


class Option(Generic[T]):
    """
    Option type representing either Some(value) or None.

    Methods:
        is_some() -> bool: True if the option contains a value.
        is_none() -> bool: True if the option is empty.
        unwrap() -> T: Returns the value, raises if None.
        unwrap_or(default: T) -> T: Returns the value or a default.
        map(func) -> Option: Maps a function over the value if present.
    """

    def __init__(self, value: Union[T, None]):
        self._value = value

    @staticmethod
    def Some(value: T) -> "Option[T]":
        return Option(value)

    @staticmethod
    def None_() -> "Option[T]":
        return Option(None)

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def unwrap(self) -> T:
        if self._value is None:
            raise RuntimeError("Called unwrap() on a None value")
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value if self._value is not None else default

    def map(self, func: Callable[[T], T]) -> "Option[T]":
        if self.is_some():
            return Option.Some(func(self._value))
        return Option.None_()


class Result(Generic[T, E]):
    """
    Result type representing either Ok(value) or Err(error).

    Methods:
        is_ok() -> bool: True if the result is Ok.
        is_err() -> bool: True if the result is Err.
        unwrap() -> T: Returns the value, raises if Err.
        unwrap_or(default: T) -> T: Returns value or a default.
        unwrap_err() -> E: Returns the error, raises if Ok.
        map(func) -> Result: Maps a function over the Ok value.
        map_err(func) -> Result: Maps a function over the Err value.
    """

    def __init__(self, ok: Union[T, None] = None, err: Union[E, None] = None):
        self._ok = ok
        self._err = err

    @staticmethod
    def Ok(value: T) -> "Result[T, E]":
        return Result(ok=value)

    @staticmethod
    def Err(error: E) -> "Result[T, E]":
        return Result(err=error)

    def is_ok(self) -> bool:
        return self._err is None

    def is_err(self) -> bool:
        return self._err is not None

    def unwrap(self) -> T:
        if self.is_err():
            raise RuntimeError(f"Unwrap failed: {self._err}")
        return self._ok

    def unwrap_or(self, default: T) -> T:
        return self._ok if self.is_ok() else default

    def unwrap_err(self) -> E:
        if self.is_ok():
            raise RuntimeError("Called unwrap_err() on an Ok value")
        return self._err

    def map(self, func: Callable[[T], T]) -> "Result[T, E]":
        if self.is_ok():
            return Result.Ok(func(self._ok))
        return Result.Err(self._err)

    def map_err(self, func: Callable[[E], E]) -> "Result[T, E]":
        if self.is_err():
            return Result.Err(func(self._err))
        return Result.Ok(self._ok)
