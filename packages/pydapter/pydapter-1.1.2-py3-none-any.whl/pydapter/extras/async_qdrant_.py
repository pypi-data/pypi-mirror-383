"""
AsyncQdrantAdapter - vector upsert / search using AsyncQdrantClient.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import grpc
from pydantic import BaseModel, ValidationError
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qd
from qdrant_client.http.exceptions import UnexpectedResponse

from ..async_core import AsyncAdapter
from ..exceptions import AdapterError, ConnectionError, QueryError, ResourceError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


class AsyncQdrantAdapter(AsyncAdapter[T]):
    """
    Asynchronous Qdrant vector database adapter for async vector operations.

    This adapter provides async methods to:
    - Search for similar vectors asynchronously and convert results to Pydantic models
    - Insert Pydantic models as vector points into Qdrant collections asynchronously
    - Handle async vector similarity operations and metadata filtering
    - Support for both cloud and self-hosted Qdrant instances with async operations

    Attributes:
        obj_key: The key identifier for this adapter type ("async_qdrant")

    Example:
        ```python
        import asyncio
        from pydantic import BaseModel
        from pydapter.extras.async_qdrant_ import AsyncQdrantAdapter

        class Document(BaseModel):
            id: str
            text: str
            embedding: list[float]
            category: str

        async def main():
            # Search for similar vectors
            search_config = {
                "url": "http://localhost:6333",
                "collection_name": "documents",
                "query_vector": [0.1, 0.2, 0.3, ...],  # 768-dim vector
                "limit": 10,
                "score_threshold": 0.8
            }
            similar_docs = await AsyncQdrantAdapter.from_obj(Document, search_config, many=True)

            # Insert documents with vectors
            insert_config = {
                "url": "http://localhost:6333",
                "collection_name": "documents"
            }
            new_docs = [Document(
                id="doc1",
                text="Sample text",
                embedding=[0.1, 0.2, 0.3, ...],
                category="tech"
            )]
            await AsyncQdrantAdapter.to_obj(new_docs, insert_config, many=True)

        asyncio.run(main())
        ```
    """

    obj_key = "async_qdrant"

    @staticmethod
    def _client(url: str | None):
        """
        Create an async Qdrant client with proper error handling.

        Args:
            url: Qdrant server URL or None for in-memory instance

        Returns:
            AsyncQdrantClient instance

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            return AsyncQdrantClient(url=url) if url else AsyncQdrantClient(":memory:")
        except UnexpectedResponse as e:
            raise ConnectionError(
                f"Failed to connect to Qdrant: {e}", adapter="async_qdrant", url=url
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Unexpected error connecting to Qdrant: {e}",
                adapter="async_qdrant",
                url=url,
            ) from e

    @staticmethod
    def _validate_vector_dimensions(vector, expected_dim=None):
        """Validate that the vector has the correct dimensions."""
        if not isinstance(vector, list | tuple) or not all(
            isinstance(x, int | float) for x in vector
        ):
            raise AdapterValidationError(
                "Vector must be a list or tuple of numbers",
                data=vector,
            )

        if expected_dim is not None and len(vector) != expected_dim:
            raise AdapterValidationError(
                f"Vector dimension mismatch: expected {expected_dim}, got {len(vector)}",
                data=vector,
            )

    # outgoing
    @classmethod
    async def to_obj(
        cls,
        subj: T | Sequence[T],
        /,
        *,
        collection,
        vector_field="embedding",
        id_field="id",
        url=None,
        many: bool = True,
        adapt_meth: str = "model_dump",
        adapt_kw: dict | None = None,
        **kw,
    ):
        try:
            # Validate required parameters
            if not collection:
                raise AdapterValidationError("Missing required parameter 'collection'")

            # Prepare data
            items = subj if isinstance(subj, Sequence) else [subj]
            if not items:
                return None  # Nothing to insert

            # Validate vector field exists
            if not hasattr(items[0], vector_field):
                raise AdapterValidationError(
                    f"Vector field '{vector_field}' not found in model",
                    data=getattr(items[0], adapt_meth)(**(adapt_kw or {})),
                )

            # Validate ID field exists
            if not hasattr(items[0], id_field):
                raise AdapterValidationError(
                    f"ID field '{id_field}' not found in model",
                    data=getattr(items[0], adapt_meth)(**(adapt_kw or {})),
                )

            # Get vector dimension
            vector = getattr(items[0], vector_field)
            cls._validate_vector_dimensions(vector)
            dim = len(vector)

            # Create client
            client = cls._client(url)

            # Create or recreate collection
            try:
                await client.recreate_collection(
                    collection,
                    vectors_config=qd.VectorParams(size=dim, distance="Cosine"),
                )
            except UnexpectedResponse as e:
                raise QueryError(
                    f"Failed to create Qdrant collection: {e}",
                    adapter="async_qdrant",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Unexpected error creating Qdrant collection: {e}",
                    adapter="async_qdrant",
                ) from e

            # Create points
            try:
                points = []
                for _i, item in enumerate(items):
                    vector = getattr(item, vector_field)
                    cls._validate_vector_dimensions(vector, dim)

                    points.append(
                        qd.PointStruct(
                            id=getattr(item, id_field),
                            vector=vector,
                            payload=getattr(item, adapt_meth)(
                                exclude={vector_field}, **(adapt_kw or {})
                            ),
                        )
                    )
            except AdapterValidationError:
                # Re-raise validation errors
                raise
            except Exception as e:
                raise AdapterValidationError(
                    f"Error creating Qdrant points: {e}",
                    data=items,
                ) from e

            # Upsert points
            try:
                await client.upsert(collection, points)
                return {"upserted_count": len(points)}
            except UnexpectedResponse as e:
                raise QueryError(
                    f"Failed to upsert points to Qdrant: {e}",
                    adapter="async_qdrant",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Unexpected error upserting points to Qdrant: {e}",
                    adapter="async_qdrant",
                ) from e

        except AdapterError:
            raise

        except Exception as e:
            raise QueryError(
                f"Unexpected error in async Qdrant adapter: {e}", adapter="async_qdrant"
            )

    # incoming
    @classmethod
    async def from_obj(
        cls,
        subj_cls: type[T],
        obj: dict,
        /,
        *,
        many=True,
        adapt_meth: str = "model_validate",
        adapt_kw: dict | None = None,
        **kw,
    ):
        try:
            if "collection" not in obj:
                raise AdapterValidationError("Missing required parameter 'collection'", data=obj)
            if "query_vector" not in obj:
                raise AdapterValidationError("Missing required parameter 'query_vector'", data=obj)

            # Validate query vector & Create client
            cls._validate_vector_dimensions(obj["query_vector"])
            client = cls._client(obj.get("url"))

            # Execute search
            try:
                res = await client.search(
                    obj["collection"],
                    obj["query_vector"],
                    limit=obj.get("top_k", 5),
                    with_payload=True,
                )
            except UnexpectedResponse as e:
                if "not found" in str(e).lower():
                    raise ResourceError(
                        f"Qdrant collection not found: {e}",
                        resource=obj["collection"],
                    ) from e
                raise QueryError(
                    f"Failed to search Qdrant: {e}",
                    adapter="async_qdrant",
                ) from e
            except grpc.RpcError as e:
                raise ConnectionError(
                    f"Qdrant RPC error: {e}",
                    adapter="async_qdrant",
                    url=obj.get("url"),
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Unexpected error searching Qdrant: {e}",
                    adapter="async_qdrant",
                ) from e

            # Extract payloads
            docs = [r.payload for r in res]

            # Handle empty result set
            if not docs:
                if many:
                    return []
                raise ResourceError(
                    "No points found matching the query vector",
                    resource=obj["collection"],
                )

            # Convert documents to model instances
            try:
                if many:
                    return [getattr(subj_cls, adapt_meth)(d, **(adapt_kw or {})) for d in docs]
                return getattr(subj_cls, adapt_meth)(docs[0], **(adapt_kw or {}))
            except ValidationError as e:
                raise AdapterValidationError(
                    f"Validation error: {e}",
                    data=docs[0] if not many else docs,
                    errors=e.errors(),
                ) from e

        except AdapterError:
            raise

        except Exception as e:
            raise QueryError(
                f"Unexpected error in async Qdrant adapter: {e}", adapter="async_qdrant"
            )
