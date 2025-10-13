# domain/selection.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Protocol, Union


"""
Selection primitives and lightweight protocols used by the domain layer.

This module intentionally defines minimal protocol surfaces so it can depend
only on interfaces, not concrete implementations. If your project already
provides concrete `Result`, `AppError`, and `RetrievalItem` types in a shared
package, you can replace these definitions with imports without changing the
rest of the code.
"""


# --- Minimal shared types ----------------------------------------------------


@dataclass
class RetrievalItem:
    """
    Minimal retrieval record returned by search backends.

    Attributes:
        doc_id: Backend-specific document identifier.
        score:  Relevance score (higher is typically better).
        metadata: Arbitrary attributes describing the hit (title, chunk info, etc.).
    """
    doc_id: str
    score: float
    metadata: Dict[str, Any]


class Result(Protocol):
    """
    Minimal `Result` protocol compatible with Rust-like result handling.

    Implementations should carry either an `ok` value or an error and expose:
      - is_ok(): bool
      - unwrap() -> Any          # returns the ok value or raises the error
      - unwrap_or(default) -> Any
    """
    def is_ok(self) -> bool: ...
    def unwrap(self) -> Any: ...
    def unwrap_or(self, default: Any) -> Any: ...


class AppError(Exception):
    """Domain-level error placeholder. Replace with your project's error type if available."""
    pass


# --- Backend protocols --------------------------------------------------------


class LexicalStore(Protocol):
    """Text-at-a-time lexical search interface (BM25/TF-IDF/etc.)."""
    def search(self, query: str, limit: int = 10) -> Result: ...


class VectorStore(Protocol):
    """Vector similarity search interface (ANN/FAISS/Qdrant/etc.)."""
    def search(self, query_vector: List[float], limit: int = 10) -> Result: ...


class TextEncoder(Protocol):
    """Text encoder interface that produces dense vectors for input strings."""
    def embed(self, text: str) -> List[float]: ...


# --- Selection results --------------------------------------------------------


class SearchOutcome(str, Enum):
    """High-level decision describing how the selection step resolved."""
    EXACT = "exact"
    OPTIONS = "options"
    NONE = "none"


@dataclass
class SelectionOptions:
    """
    Tuning knobs for selection behavior.

    Attributes:
        top_k_options: Used only for OPTIONS outcome; number of candidates to surface.
        lex_weight: Weight applied to lexical scores when mixing signals.
        vec_weight: Weight applied to vector scores when mixing signals.
        exact_cover: Fraction [0.0, 1.0] of query tokens that must be present for EXACT.
        options_min_cover: Minimum token coverage required for OPTIONS candidates.
        require_attrs: If True, candidates must provide required attributes in metadata.
    """
    top_k_options: int = 3
    lex_weight: float = 1.7
    vec_weight: float = 1.0
    exact_cover: float = 1.0
    options_min_cover: float = 0.5
    require_attrs: bool = False


@dataclass
class SelectionResult:
    """
    Final selection decision plus context payload.

    Context shape by outcome:
        - SearchOutcome.EXACT:   `context` is a `str` containing the chosen `doc_id`.
        - SearchOutcome.OPTIONS: `context` is `List[Dict[str, Any]]` with fields like
                                 {"doc_id": str, "name": str, "score": float, ...}.
        - SearchOutcome.NONE:    `context` is `None` (no suitable candidates).

    Attributes:
        outcome: The resolved outcome category.
        context: Payload matching the shape described above.
    """
    outcome: SearchOutcome
    context: Union[str, List[Dict[str, Any]], None]
