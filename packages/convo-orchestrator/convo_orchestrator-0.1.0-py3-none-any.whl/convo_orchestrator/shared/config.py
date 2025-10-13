#shared/config.py
"""
Environment-backed configuration with dotenv support.

This module defines a singleton `Config` responsible for loading environment
variables (via python-dotenv) and providing typed accessors. It attempts to
coerce values into sensible Python types: dict, list, set, bool, int, float,
or str. Consumers receive Rust-like `Result[T, AppError]` for safe handling.

Usage:
    from shared.config import Config

    cfg = Config.instance()  # singleton
    port_res = cfg.get("PORT", expected_type=int, default=8080)
    port = port_res.unwrap()  # or handle Err

    secret = cfg.require("SECRET_KEY").unwrap()  # fails if missing
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, Optional, Set, Tuple, Type, TypeVar

from dotenv import load_dotenv

from . import AppError, ErrorKind
from . import Result

T = TypeVar("T")


def _strip_quotes(s: str) -> str:
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _parse_bool(s: str) -> Optional[bool]:
    v = s.strip().lower()
    if v in ("true", "1", "yes", "y", "on"): return True
    if v in ("false", "0", "no", "n", "off"): return False
    return None


def _parse_json(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


def _parse_list_from_csv(s: str) -> Optional[list[str]]:
    if "," in s:
        return [item.strip() for item in s.split(",")]
    return None


def _parse_set(s: str) -> Optional[Set[str]]:
    # Accept forms like: "{a,b,c}" or "a,b,c" (when expected_type is set)
    ss = s.strip()
    if ss.startswith("{") and ss.endswith("}"):
        content = ss[1:-1]
        return {item.strip() for item in content.split(",")} if content else set()
    if "," in ss:
        return {item.strip() for item in ss.split(",")}
    return None


def _coerce(value: str, expected_type: Optional[Type[T]] = None) -> Result[T, AppError]:
    """
    Try to coerce the raw string into the expected_type if provided,
    otherwise auto-detect the most natural type.

    Auto-detect order:
        1) JSON (dict, list, number, bool, null)
        2) bool ("true/false/1/0/yes/no/on/off")
        3) int
        4) float
        5) CSV -> list[str]
        6) str

    Special-cases when expected_type is `set`: tries "{a,b}" or CSV to set[str].
    """
    raw = _strip_quotes(value)

    # If a target type is specified, try to meet it exactly.
    if expected_type is not None:
        try:
            if expected_type is bool:
                parsed = _parse_bool(raw)
                if parsed is None:
                    raise ValueError("Not a boolean literal")
                return Result.Ok(parsed)  # type: ignore[arg-type]

            if expected_type is int:
                return Result.Ok(int(raw))  # type: ignore[arg-type]

            if expected_type is float:
                return Result.Ok(float(raw))  # type: ignore[arg-type]

            if expected_type is str:
                return Result.Ok(raw)  # type: ignore[arg-type]

            if expected_type is list:
                # Prefer JSON lists; fallback to CSV
                j = _parse_json(raw)
                if isinstance(j, list):
                    return Result.Ok(j)  # type: ignore[arg-type]
                csv_list = _parse_list_from_csv(raw)
                if csv_list is not None:
                    return Result.Ok(csv_list)  # type: ignore[arg-type]
                return Result.Err(AppError(ErrorKind.VALIDATION, f"Cannot parse list from '{raw}'"))

            if expected_type is dict:
                j = _parse_json(raw)
                if isinstance(j, dict):
                    return Result.Ok(j)  # type: ignore[arg-type]
                return Result.Err(AppError(ErrorKind.VALIDATION, f"Cannot parse dict from '{raw}'"))

            if expected_type is set:
                s = _parse_set(raw)
                if s is not None:
                    return Result.Ok(s)  # type: ignore[arg-type]
                return Result.Err(AppError(ErrorKind.VALIDATION, f"Cannot parse set from '{raw}'"))

            # If expected_type is something else, try JSON first then direct cast
            j = _parse_json(raw)
            if j is not None and isinstance(j, expected_type):
                return Result.Ok(j)
            # Last resort: try to call the type on the string
            return Result.Ok(expected_type(raw))  # type: ignore[misc]

        except Exception as ex:
            return Result.Err(AppError(ErrorKind.VALIDATION, f"Failed to coerce '{raw}' to {getattr(expected_type, '__name__', expected_type)}: {ex}"))

    # Auto-detect mode
    j = _parse_json(raw)
    if j is not None:
        # Map JSON null -> None, but we still return it (caller decides)
        return Result.Ok(j)  # type: ignore[return-value]

    b = _parse_bool(raw)
    if b is not None:
        return Result.Ok(b)  # type: ignore[return-value]

    try:
        return Result.Ok(int(raw))  # type: ignore[return-value]
    except Exception:
        pass

    try:
        return Result.Ok(float(raw))  # type: ignore[return-value]
    except Exception:
        pass

    csv_list = _parse_list_from_csv(raw)
    if csv_list is not None:
        return Result.Ok(csv_list)  # type: ignore[return-value]

    return Result.Ok(raw)  # type: ignore[return-value]


class Config:
    """
    Singleton configuration service.

    Responsibilities:
        - Load `.env` (if present) using python-dotenv (only once).
        - Provide typed getters backed by os.environ.
        - Return values wrapped in Result[T, AppError] for safety.
        - Cache successful lookups to minimize overhead.

    Environment variable parsing supports:
        - dict/list via JSON
        - set via "{a,b,c}" or CSV when expected_type=set
        - bool: true/false/1/0/yes/no/on/off
        - int, float, str

    Class methods:
        instance() -> Config  : obtain the singleton
    """

    _instance: Optional["Config"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):  # prevent direct instantiation
        raise RuntimeError("Use Config.instance()")

    @classmethod
    def instance(cls, dotenv_path: Optional[str] = None, override: bool = False) -> "Config":
        """
        Get the Config singleton. Loads .env once (or with override=True).
        """
        with cls._lock:
            if cls._instance is None:
                # Bypass __new__/__init__ ban
                obj = super().__new__(cls)
                # Load dotenv early; do not crash if missing
                load_dotenv(dotenv_path, override=override)
                obj._cache: Dict[Tuple[str, Optional[type]], Any] = {} # type: ignore
                obj._loaded_path = dotenv_path
                obj._override = override
                cls._instance = obj
            else:
                # Optionally reload .env when caller explicitly asks for override
                if override and dotenv_path != cls._instance._loaded_path:
                    load_dotenv(dotenv_path, override=True)
                    cls._instance._loaded_path = dotenv_path
                    cls._instance._cache.clear()
            return cls._instance

    # ---------------- API ----------------

    def get(
        self,
        name: str,
        expected_type: Optional[Type[T]] = None,
        default: Optional[T] = None,
    ) -> Result[T, AppError]:
        """
        Retrieve an environment variable by name.

        Args:
            name: Variable name.
            expected_type: Optional target type for coercion.
            default: Optional default value if missing or empty.

        Returns:
            Result[T, AppError]: Ok(value) if found (or default applied),
            otherwise Err(AppError(kind=NOT_FOUND)).
        """
        key = (name, expected_type)
        if key in self._cache:
            return Result.Ok(self._cache[key])  # type: ignore[return-value]

        raw = os.environ.get(name, None)
        if raw is None or raw == "":
            if default is not None:
                self._cache[key] = default
                return Result.Ok(default)
            return Result.Err(AppError(ErrorKind.NOT_FOUND, f"Environment variable '{name}' not set"))

        coerced = _coerce(raw, expected_type)
        if coerced.is_ok():
            val = coerced.unwrap()
            self._cache[key] = val
            return Result.Ok(val)
        else:
            # If coercion fails and default is provided, fallback to default
            if default is not None:
                self._cache[key] = default
                return Result.Ok(default)
            return Result.Err(coerced.unwrap_err())

    def require(self, name: str, expected_type: Optional[Type[T]] = None) -> Result[T, AppError]:
        """
        Retrieve a required variable. Fails if missing or bad format.

        Returns:
            Ok(value) or Err(AppError)
        """
        res = self.get(name, expected_type=expected_type, default=None)
        if res.is_ok():
            val = res.unwrap()
            if val is None:
                return Result.Err(AppError(ErrorKind.VALIDATION, f"Required variable '{name}' is null"))
            return Result.Ok(val)
        return Result.Err(res.unwrap_err())

    def as_dict(self) -> Dict[str, str]:
        """
        Return the effective environment (os.environ) as a plain dictionary of strings.
        This does not apply coercion, only exposes raw values.
        """
        return dict(os.environ)
