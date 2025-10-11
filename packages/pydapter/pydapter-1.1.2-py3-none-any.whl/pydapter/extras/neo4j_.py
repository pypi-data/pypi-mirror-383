"""
Neo4j adapter (requires `neo4j`).
"""

from __future__ import annotations

from collections.abc import Sequence
import re
from typing import TypeVar

import neo4j
from neo4j import GraphDatabase
import neo4j.exceptions
from pydantic import BaseModel, ValidationError

from ..core import Adapter
from ..exceptions import ConnectionError, QueryError, ResourceError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


class Neo4jAdapter(Adapter[T]):
    """
    Neo4j graph database adapter for converting between Pydantic models and Neo4j nodes/relationships.

    This adapter provides methods to:
    - Execute Cypher queries and convert results to Pydantic models
    - Create nodes and relationships from Pydantic models
    - Handle Neo4j connection management and error handling
    - Support for complex graph operations and traversals

    Attributes:
        obj_key: The key identifier for this adapter type ("neo4j")

    Example:
        ```python
        from pydantic import BaseModel
        from pydapter.extras.neo4j_ import Neo4jAdapter
        from neo4j import basic_auth

        class Person(BaseModel):
            name: str
            age: int
            city: str

        # Query from Neo4j
        query_config = {
            "url": "bolt://localhost:7687",
            "auth": basic_auth("neo4j", "password"),
            "query": "MATCH (p:Person) WHERE p.age >= 18 RETURN p.name, p.age, p.city"
        }
        people = Neo4jAdapter.from_obj(Person, query_config, many=True)

        # Create nodes in Neo4j
        create_config = {
            "url": "bolt://localhost:7687",
            "auth": basic_auth("neo4j", "password"),
            "query": "CREATE (p:Person {name: $name, age: $age, city: $city})"
        }
        new_people = [Person(name="John", age=30, city="NYC")]
        Neo4jAdapter.to_obj(new_people, create_config, many=True)
        ```
    """

    obj_key = "neo4j"

    @classmethod
    def _create_driver(cls, url: str, auth=None) -> neo4j.Driver:
        """
        Create a Neo4j driver with proper error handling.

        Args:
            url: Neo4j connection URL (e.g., "bolt://localhost:7687")
            auth: Authentication tuple or None for no auth

        Returns:
            neo4j.Driver instance

        Raises:
            ConnectionError: If connection cannot be established or auth fails
        """
        try:
            if auth:
                return GraphDatabase.driver(url, auth=auth)
            else:
                return GraphDatabase.driver(url)
        except neo4j.exceptions.ServiceUnavailable as e:
            raise ConnectionError(
                f"Neo4j service unavailable: {e}", adapter="neo4j", url=url
            ) from e
        except neo4j.exceptions.AuthError as e:
            raise ConnectionError(
                f"Neo4j authentication failed: {e}", adapter="neo4j", url=url
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Failed to create Neo4j driver: {e}", adapter="neo4j", url=url
            ) from e

    @classmethod
    def _validate_cypher(cls, cypher: str) -> None:
        """Basic validation for Cypher queries to prevent injection."""
        # Check for unescaped backticks in label names
        if re.search(r"`[^`]*`[^`]*`", cypher):
            raise QueryError(
                "Invalid Cypher query: Possible injection in label name",
                query=cypher,
                adapter="neo4j",
            )

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

            # Create driver
            auth = obj.get("auth")
            driver = cls._create_driver(obj["url"], auth=auth)

            # Prepare Cypher query
            label = obj.get("label", subj_cls.__name__)
            where = f"WHERE {obj['where']}" if "where" in obj else ""
            cypher = f"MATCH (n:`{label}`) {where} RETURN n"

            # Validate Cypher query
            cls._validate_cypher(cypher)

            # Execute query
            try:
                with driver.session() as s:
                    result = s.run(cypher)
                    rows = [r["n"]._properties for r in result]
            except neo4j.exceptions.CypherSyntaxError as e:
                raise QueryError(
                    f"Neo4j Cypher syntax error: {e}",
                    query=cypher,
                    adapter="neo4j",
                ) from e
            except neo4j.exceptions.ClientError as e:
                if "not found" in str(e).lower():
                    raise ResourceError(
                        f"Neo4j resource not found: {e}",
                        resource=label,
                    ) from e
                raise QueryError(
                    f"Neo4j client error: {e}",
                    query=cypher,
                    adapter="neo4j",
                ) from e
            except Exception as e:
                raise QueryError(
                    f"Error executing Neo4j query: {e}",
                    query=cypher,
                    adapter="neo4j",
                ) from e
            finally:
                driver.close()

            # Handle empty result set
            if not rows:
                if many:
                    return []
                raise ResourceError(
                    "No nodes found matching the query",
                    resource=label,
                    where=obj.get("where", ""),
                )

            # Convert rows to model instances
            try:
                if many:
                    return [getattr(subj_cls, adapt_meth)(r, **(adapt_kw or {})) for r in rows]
                return getattr(subj_cls, adapt_meth)(rows[0], **(adapt_kw or {}))
            except ValidationError as e:
                raise AdapterValidationError(
                    f"Validation error: {e}",
                    data=rows[0] if not many else rows,
                    errors=e.errors(),
                ) from e

        except (ConnectionError, QueryError, ResourceError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise QueryError(f"Unexpected error in Neo4j adapter: {e}", adapter="neo4j")

    # outgoing
    @classmethod
    def to_obj(
        cls,
        subj: T | Sequence[T],
        /,
        *,
        url,
        auth=None,
        label=None,
        merge_on="id",
        many: bool = True,
        adapt_meth: str = "model_dump",
        adapt_kw: dict | None = None,
        **kw,
    ):
        try:
            # Validate required parameters
            if not url:
                raise AdapterValidationError("Missing required parameter 'url'")
            if not merge_on:
                raise AdapterValidationError("Missing required parameter 'merge_on'")

            # Prepare data
            items = subj if isinstance(subj, Sequence) else [subj]
            if not items:
                return None  # Nothing to insert

            # Get label from first item if not provided
            label = label or items[0].__class__.__name__

            # Create driver
            driver = cls._create_driver(url, auth=auth)

            try:
                with driver.session() as s:
                    results = []
                    for it in items:
                        props = getattr(it, adapt_meth)(**(adapt_kw or {}))

                        # Check if merge_on property exists
                        if merge_on not in props:
                            raise AdapterValidationError(
                                f"Merge property '{merge_on}' not found in model",
                                data=props,
                            )

                        # Prepare and validate Cypher query
                        cypher = f"MERGE (n:`{label}` {{{merge_on}: $val}}) SET n += $props"
                        cls._validate_cypher(cypher)

                        # Execute query
                        try:
                            result = s.run(cypher, val=props[merge_on], props=props)
                            results.append(result)
                        except neo4j.exceptions.CypherSyntaxError as e:
                            raise QueryError(
                                f"Neo4j Cypher syntax error: {e}",
                                query=cypher,
                                adapter="neo4j",
                            ) from e
                        except neo4j.exceptions.ConstraintError as e:
                            raise QueryError(
                                f"Neo4j constraint violation: {e}",
                                query=cypher,
                                adapter="neo4j",
                            ) from e
                        except Exception as e:
                            raise QueryError(
                                f"Error executing Neo4j query: {e}",
                                query=cypher,
                                adapter="neo4j",
                            ) from e

                    return {"merged_count": len(results)}
            finally:
                driver.close()

        except (ConnectionError, QueryError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise QueryError(f"Unexpected error in Neo4j adapter: {e}", adapter="neo4j")
