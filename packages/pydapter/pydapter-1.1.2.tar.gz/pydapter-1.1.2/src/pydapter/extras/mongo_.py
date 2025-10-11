"""
MongoDB adapter (requires `pymongo`).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel, ValidationError
import pymongo
from pymongo import MongoClient
import pymongo.errors

from ..core import Adapter
from ..exceptions import AdapterError, ConnectionError, QueryError, ResourceError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


__all__ = (
    "MongoAdapter",
    "MongoClient",
)


class MongoAdapter(Adapter[T]):
    """
    MongoDB adapter for converting between Pydantic models and MongoDB documents.

    This adapter provides methods to:
    - Query MongoDB collections and convert documents to Pydantic models
    - Insert Pydantic models as documents into MongoDB collections
    - Handle MongoDB connection management and error handling
    - Support for various MongoDB operations (find, insert, update, delete)

    Attributes:
        obj_key: The key identifier for this adapter type ("mongo")

    Example:
        ```python
        from pydantic import BaseModel
        from pydapter.extras.mongo_ import MongoAdapter

        class User(BaseModel):
            name: str
            email: str
            age: int

        # Query from MongoDB
        query_config = {
            "url": "mongodb://localhost:27017",
            "database": "myapp",
            "collection": "users",
            "filter": {"age": {"$gte": 18}}
        }
        users = MongoAdapter.from_obj(User, query_config, many=True)

        # Insert to MongoDB
        insert_config = {
            "url": "mongodb://localhost:27017",
            "database": "myapp",
            "collection": "users"
        }
        new_users = [User(name="John", email="john@example.com", age=30)]
        MongoAdapter.to_obj(new_users, insert_config, many=True)
        ```
    """

    obj_key = "mongo"

    @classmethod
    def _client(cls, url: str) -> pymongo.MongoClient:
        """
        Create a MongoDB client with proper error handling.

        Args:
            url: MongoDB connection string

        Returns:
            pymongo.MongoClient instance

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            return pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
        except pymongo.errors.ConfigurationError as e:
            raise ConnectionError(
                f"Invalid MongoDB connection string: {e}", adapter="mongo", url=url
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Failed to create MongoDB client: {e}", adapter="mongo", url=url
            ) from e

    @classmethod
    def _validate_connection(cls, client: pymongo.MongoClient) -> None:
        """Validate that the MongoDB connection is working."""
        try:
            # This will raise an exception if the connection fails
            client.admin.command("ping")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            raise ConnectionError(f"MongoDB server selection timeout: {e}", adapter="mongo") from e
        except pymongo.errors.OperationFailure as e:
            if "auth failed" in str(e).lower():
                raise ConnectionError(f"MongoDB authentication failed: {e}", adapter="mongo") from e
            raise QueryError(f"MongoDB operation failure: {e}", adapter="mongo") from e
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}", adapter="mongo") from e

    # incoming
    @classmethod
    def from_obj(
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
            cls._validate_connection(client)

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

                docs = list(coll.find(filter_query))
            except pymongo.errors.OperationFailure as e:
                if "not authorized" in str(e).lower():
                    raise ConnectionError(
                        f"Not authorized to access {obj['db']}.{obj['collection']}: {e}",
                        adapter="mongo",
                        url=obj["url"],
                    ) from e
                raise QueryError(
                    f"MongoDB query error: {e}",
                    query=filter_query,
                    adapter="mongo",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Error executing MongoDB query: {e}",
                    query=filter_query,
                    adapter="mongo",
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

        except AdapterError:
            raise

        except Exception as e:
            raise QueryError(f"Unexpected error in MongoDB adapter: {e}", adapter="mongo")

    # outgoing
    @classmethod
    def to_obj(
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
            cls._validate_connection(client)

            # Prepare data
            items = subj if isinstance(subj, Sequence) else [subj]
            if not items:
                return None  # Nothing to insert

            payload = [getattr(i, adapt_meth)(**(adapt_kw or {})) for i in items]

            # Execute insert
            try:
                result = client[db][collection].insert_many(payload)
                return {"inserted_count": result.inserted_ids}
            except pymongo.errors.BulkWriteError as e:
                raise QueryError(
                    f"MongoDB bulk write error: {e}",
                    adapter="mongo",
                ) from e
            except pymongo.errors.OperationFailure as e:
                if "not authorized" in str(e).lower():
                    raise ConnectionError(
                        f"Not authorized to write to {db}.{collection}: {e}",
                        adapter="mongo",
                        url=url,
                    ) from e
                raise QueryError(
                    f"MongoDB operation failure: {e}",
                    adapter="mongo",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Error inserting documents into MongoDB: {e}",
                    adapter="mongo",
                ) from e

        except AdapterError:
            raise

        except Exception as e:
            # Wrap other exceptions
            raise QueryError(f"Unexpected error in MongoDB adapter: {e}", adapter="mongo")
