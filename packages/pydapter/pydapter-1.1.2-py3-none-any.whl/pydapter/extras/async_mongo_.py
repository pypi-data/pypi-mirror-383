"""
AsyncMongoAdapter - uses `motor.motor_asyncio`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ValidationError
import pymongo
from pymongo import MongoClient
import pymongo.errors

from ..async_core import AsyncAdapter
from ..exceptions import ConnectionError, QueryError, ResourceError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


__all__ = (
    "AsyncMongoAdapter",
    "MongoClient",
)


class AsyncMongoAdapter(AsyncAdapter[T]):
    """
    Asynchronous MongoDB adapter for converting between Pydantic models and MongoDB documents.

    This adapter provides async methods to:
    - Query MongoDB collections asynchronously and convert documents to Pydantic models
    - Insert Pydantic models as documents into MongoDB collections asynchronously
    - Handle async MongoDB operations using Motor (async MongoDB driver)
    - Support for various async MongoDB operations (find, insert, update, delete)

    Attributes:
        obj_key: The key identifier for this adapter type ("async_mongo")

    Example:
        ```python
        import asyncio
        from pydantic import BaseModel
        from pydapter.extras.async_mongo_ import AsyncMongoAdapter

        class User(BaseModel):
            name: str
            email: str
            age: int

        async def main():
            # Query from MongoDB
            query_config = {
                "url": "mongodb://localhost:27017",
                "database": "myapp",
                "collection": "users",
                "filter": {"age": {"$gte": 18}}
            }
            users = await AsyncMongoAdapter.from_obj(User, query_config, many=True)

            # Insert to MongoDB
            insert_config = {
                "url": "mongodb://localhost:27017",
                "database": "myapp",
                "collection": "users"
            }
            new_users = [User(name="John", email="john@example.com", age=30)]
            await AsyncMongoAdapter.to_obj(new_users, insert_config, many=True)

        asyncio.run(main())
        ```
    """

    obj_key = "async_mongo"

    @classmethod
    def _client(cls, url: str) -> AsyncIOMotorClient:
        try:
            return AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        except pymongo.errors.ConfigurationError as e:
            raise ConnectionError(
                f"Invalid MongoDB connection string: {e}",
                adapter="async_mongo",
                url=url,
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Failed to create MongoDB client: {e}", adapter="async_mongo", url=url
            ) from e

    @classmethod
    async def _validate_connection(cls, client: AsyncIOMotorClient) -> None:
        """Validate that the MongoDB connection is working."""
        try:
            # This will raise an exception if the connection fails
            await client.admin.command("ping")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            raise ConnectionError(
                f"MongoDB server selection timeout: {e}", adapter="async_mongo"
            ) from e
        except pymongo.errors.OperationFailure as e:
            if "auth failed" in str(e).lower():
                raise ConnectionError(
                    f"MongoDB authentication failed: {e}", adapter="async_mongo"
                ) from e
            raise QueryError(f"MongoDB operation failure: {e}", adapter="async_mongo") from e
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to MongoDB: {e}", adapter="async_mongo"
            ) from e

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
            # Validate required parameters
            if "url" not in obj:
                raise AdapterValidationError("Missing required parameter 'url'", data=obj)
            if "db" not in obj:
                raise AdapterValidationError("Missing required parameter 'db'", data=obj)
            if "collection" not in obj:
                raise AdapterValidationError("Missing required parameter 'collection'", data=obj)

            # Create client and validate connection
            client = cls._client(obj["url"])
            await cls._validate_connection(client)

            # Get collection and execute query
            try:
                coll = client[obj["db"]][obj["collection"]]
                filter_query = obj.get("filter") or {}

                # Validate filter query if provided
                if filter_query and not isinstance(filter_query, dict):
                    raise AdapterValidationError(
                        "Filter must be a dictionary",
                        data=filter_query,
                    )

                docs = await coll.find(filter_query).to_list(length=None)
            except pymongo.errors.OperationFailure as e:
                if "not authorized" in str(e).lower():
                    raise ConnectionError(
                        f"Not authorized to access {obj['db']}.{obj['collection']}: {e}",
                        adapter="async_mongo",
                        url=obj["url"],
                    ) from e
                raise QueryError(
                    f"MongoDB query error: {e}",
                    query=filter_query,
                    adapter="async_mongo",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Error executing MongoDB query: {e}",
                    query=filter_query,
                    adapter="async_mongo",
                ) from e

            # Handle empty result set
            if not docs:
                if many:
                    return []
                raise ResourceError(
                    "No documents found matching the query",
                    resource=f"{obj['db']}.{obj['collection']}",
                    filter=filter_query,
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

        except (ConnectionError, QueryError, ResourceError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise QueryError(
                f"Unexpected error in async MongoDB adapter: {e}", adapter="async_mongo"
            )

    # outgoing
    @classmethod
    async def to_obj(
        cls,
        subj: T | Sequence[T],
        /,
        *,
        url,
        db,
        collection,
        many=True,
        adapt_meth: str = "model_dump",
        adapt_kw: dict | None = None,
        **kw,
    ):
        try:
            # Validate required parameters
            if not url:
                raise AdapterValidationError("Missing required parameter 'url'")
            if not db:
                raise AdapterValidationError("Missing required parameter 'db'")
            if not collection:
                raise AdapterValidationError("Missing required parameter 'collection'")

            # Create client and validate connection
            client = cls._client(url)
            await cls._validate_connection(client)

            # Prepare data
            items = subj if isinstance(subj, Sequence) else [subj]
            if not items:
                return None  # Nothing to insert

            payload = [getattr(i, adapt_meth)(**(adapt_kw or {})) for i in items]

            # Execute insert
            try:
                result = await client[db][collection].insert_many(payload)
                return {"inserted_count": len(result.inserted_ids)}
            except pymongo.errors.BulkWriteError as e:
                raise QueryError(
                    f"MongoDB bulk write error: {e}",
                    adapter="async_mongo",
                ) from e
            except pymongo.errors.OperationFailure as e:
                if "not authorized" in str(e).lower():
                    raise ConnectionError(
                        f"Not authorized to write to {db}.{collection}: {e}",
                        adapter="async_mongo",
                        url=url,
                    ) from e
                raise QueryError(
                    f"MongoDB operation failure: {e}",
                    adapter="async_mongo",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Error inserting documents into MongoDB: {e}",
                    adapter="async_mongo",
                ) from e

        except (ConnectionError, QueryError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise QueryError(
                f"Unexpected error in async MongoDB adapter: {e}", adapter="async_mongo"
            )
