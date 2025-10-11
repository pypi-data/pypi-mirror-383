"""
JSON Adapter for Pydantic Models.

This module provides the JsonAdapter class for converting between Pydantic models
and JSON data formats. It supports reading from JSON files, strings, or bytes
and writing Pydantic models to JSON format.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from ..core import Adapter
from ..exceptions import ParseError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


class JsonAdapter(Adapter[T]):
    """
    Adapter for converting between Pydantic models and JSON data.

    This adapter handles JSON files, strings, and byte data, providing methods to:
    - Parse JSON data into Pydantic model instances
    - Convert Pydantic models to JSON format
    - Handle both single objects and arrays of objects

    Attributes:
        obj_key: The key identifier for this adapter type ("json")

    Example:
        ```python
        from pydantic import BaseModel
        from pydapter.adapters.json_ import JsonAdapter

        class Person(BaseModel):
            name: str
            age: int

        # Parse JSON data
        json_data = '{"name": "John", "age": 30}'
        person = JsonAdapter.from_obj(Person, json_data)

        # Parse JSON array
        json_array = '[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]'
        people = JsonAdapter.from_obj(Person, json_array, many=True)

        # Convert to JSON
        json_output = JsonAdapter.to_obj(person)
        ```
    """

    obj_key = "json"

    # ---------------- incoming
    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | bytes | Path,
        /,
        *,
        many=False,
        adapt_meth: str = "model_validate",
        adapt_kw: dict | None = None,
        **kw,
    ):
        try:
            # Handle file path
            if isinstance(obj, Path):
                try:
                    text = Path(obj).read_text()
                except Exception as e:
                    raise ParseError(f"Failed to read JSON file: {e}", source=str(obj))
            else:
                text = obj.decode("utf-8") if isinstance(obj, bytes) else obj
            # Check for empty input
            if not text or (isinstance(text, str) and not text.strip()):
                raise ParseError(
                    "Empty JSON content",
                    source=str(obj)[:100] if isinstance(obj, str) else str(obj),
                )

            # Parse JSON
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                raise ParseError(
                    f"Invalid JSON: {e}",
                    source=str(text)[:100] if isinstance(text, str) else str(text),
                    position=e.pos,
                    line=e.lineno,
                    column=e.colno,
                )

            # Validate against model
            try:
                if many:
                    if not isinstance(data, list):
                        raise AdapterValidationError("Expected JSON array for many=True", data=data)
                    return [getattr(subj_cls, adapt_meth)(i, **(adapt_kw or {})) for i in data]
                return getattr(subj_cls, adapt_meth)(data, **(adapt_kw or {}))
            except ValidationError as e:
                raise AdapterValidationError(
                    f"Validation error: {e}",
                    data=data,
                    errors=e.errors(),
                )

        except (ParseError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ParseError(
                f"Unexpected error parsing JSON: {e}",
                source=str(obj)[:100] if isinstance(obj, str) else str(obj),
            )

    # ---------------- outgoing
    @classmethod
    def to_obj(
        cls,
        subj: T | list[T],
        /,
        *,
        many=False,
        adapt_meth: str = "model_dump",
        adapt_kw: dict | None = None,
        **kw,
    ) -> str:
        try:
            items = subj if isinstance(subj, list) else [subj]

            if not items:
                return "[]" if many else "{}"

            # Extract JSON serialization options from kwargs
            json_kwargs = {
                "indent": kw.pop("indent", 2),
                "sort_keys": kw.pop("sort_keys", True),
                "ensure_ascii": kw.pop("ensure_ascii", False),
            }

            payload = (
                [getattr(i, adapt_meth)(**(adapt_kw or {})) for i in items]
                if many
                else getattr(items[0], adapt_meth)(**(adapt_kw or {}))
            )
            return json.dumps(payload, **json_kwargs)

        except Exception as e:
            # Wrap exceptions
            raise ParseError(f"Error generating JSON: {e}")
