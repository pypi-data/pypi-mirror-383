# adapters/qdrant_store.py
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Batch, Distance, FieldCondition, Filter, MatchValue, VectorParams

from ..shared import Result, AppError, ErrorKind, LogBus
from ..domain.rag_domain import VectorStore, RetrievalItem


class QdrantVectorStore(VectorStore):
    """
    Qdrant-backed VectorStore adapter.

    Features:
        - Lazily creates the collection (optional) with the configured vector size and distance.
        - Upserts batches with deterministic UUIDv5 IDs derived from (collection, doc_id).
        - Searches via `query_points` when available; falls back to legacy `search` for older clients.
        - Supports simple payload filtering using exact-value matches.

    Notes on compatibility:
        - Some older qdrant-client versions do not support `query_points`; we detect this and use `search`.
        - When filtering is provided, we use the legacy `search` path that accepts `query_filter`.
    """

    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        https: bool = False,
        api_key: Optional[str] = None,
        vector_size: Optional[int] = None,
        distance: str = "Cosine",
        on_missing_create: bool = True,
        log_topic: str = "rag.qdrant",
    ) -> None:
        self._collection = collection
        self._vector_size = vector_size
        self._distance = distance
        self._create = on_missing_create
        self._log = LogBus.instance().topic(log_topic)
        self._cli = QdrantClient(host=host, port=port, https=https, api_key=api_key)

    def _point_id(self, doc_id: str) -> str:
        """Deterministic UUIDv5 for the given (collection, doc_id)."""
        return str(uuid5(NAMESPACE_URL, f"qdrant:{self._collection}:{doc_id}"))

    def ensure_collection(self) -> Result[None, AppError]:
        """
        Ensure the target collection exists (optionally creating it).

        Returns:
            Ok(None) on success or Err(AppError) on failure.
        """
        try:
            dist = getattr(Distance, self._distance.upper(), Distance.COSINE)
            if not self._cli.collection_exists(self._collection):
                if not self._create:
                    return Result.Err(
                        AppError(ErrorKind.NOT_FOUND, f"Qdrant collection '{self._collection}' not found")
                    )
                if self._vector_size is None:
                    return Result.Err(
                        AppError(ErrorKind.BAD_REQUEST, "vector_size must be provided when creating collection")
                    )

                self._cli.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(size=int(self._vector_size), distance=dist),
                )
                self._log.info(
                    lambda: f"qdrant collection created name={self._collection} size={self._vector_size} dist={self._distance}"
                )
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"qdrant ensure_collection: {ex}"))

    def upsert_many(self, items: Iterable[Tuple[str, List[float], Dict[str, Any]]]) -> Result[None, AppError]:
        """
        Upsert a batch of points.

        Args:
            items: Iterable of (doc_id, vector, metadata).

        Returns:
            Ok(None) on success or Err(AppError) on failure.
        """
        try:
            coll_res = self.ensure_collection()
            if coll_res.is_err():
                return Result.Err(coll_res.unwrap_err())

            ids: List[str] = []
            vectors: List[List[float]] = []
            payloads: List[Dict[str, Any]] = []

            for doc_id, vec, meta in items:
                ids.append(self._point_id(doc_id))
                vectors.append(vec)
                merged = dict(meta or {})
                merged["_doc_id"] = doc_id
                payloads.append(merged)

            batch = Batch(ids=ids, vectors=vectors, payloads=payloads)
            self._cli.upsert(collection_name=self._collection, points=batch)
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"qdrant upsert_many: {ex}"))

    def remove(self, doc_id: str) -> Result[None, AppError]:
        """
        Remove a single point by its original document ID.

        Args:
            doc_id: Original document identifier.

        Returns:
            Ok(None) on success or Err(AppError) on failure.
        """
        try:
            pid = self._point_id(doc_id)
            self._cli.delete(collection_name=self._collection, points_selector={"points": [pid]})
            return Result.Ok(None)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"qdrant remove: {ex}"))

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter_payload: Optional[Dict[str, Any]] = None,
    ) -> Result[List[RetrievalItem], AppError]:
        """
        Search for nearest neighbors and return standardized retrieval items.

        Args:
            query_vector: Dense query vector.
            limit: Maximum number of hits to return.
            filter_payload: Optional payload filter (exact-value matches).

        Returns:
            Ok(list of RetrievalItem) on success or Err(AppError) on failure.
        """
        try:
            qfilter = None
            if filter_payload:
                qfilter = Filter(
                    must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter_payload.items()]
                )

            hits = None

            # Prefer modern API when no filter is needed. Older clients may not have `query_points`.
            if qfilter is None:
                try:
                    resp = self._cli.query_points(
                        collection_name=self._collection,
                        query=query_vector,
                        limit=limit,
                    )
                    hits = resp.points
                except AttributeError:
                    # Fallback for older clients: use legacy search() without filter.
                    hits = self._cli.search(
                        collection_name=self._collection,
                        query_vector=query_vector,
                        limit=limit,
                        query_filter=None,
                        with_payload=True,
                    )
            else:
                # When a filter is provided, use legacy search() path that accepts `query_filter`.
                hits = self._cli.search(
                    collection_name=self._collection,
                    query_vector=query_vector,
                    limit=limit,
                    query_filter=qfilter,
                    with_payload=True,
                )

            items: List[RetrievalItem] = []
            for h in hits:
                meta = dict(getattr(h, "payload", {}) or {})
                orig_id = meta.get("_doc_id", str(getattr(h, "id", "")))
                items.append(
                    RetrievalItem(
                        doc_id=orig_id,
                        score=float(getattr(h, "score", 0.0) or 0.0),
                        metadata=meta,
                    )
                )
            return Result.Ok(items)
        except Exception as ex:
            return Result.Err(AppError(ErrorKind.REPOSITORY_ERROR, f"qdrant search: {ex}"))
