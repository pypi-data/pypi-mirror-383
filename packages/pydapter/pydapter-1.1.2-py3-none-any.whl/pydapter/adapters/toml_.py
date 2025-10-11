"""
TOML Adapter for Pydantic Models.

This module provides the TomlAdapter class for converting between Pydantic models
and TOML data formats. It supports reading from TOML files or strings and writing
Pydantic models to TOML format.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError
import toml

from ..core import Adapter
from ..exceptions import ParseError
from ..exceptions import ValidationError as AdapterValidationError

T = TypeVar("T", bound=BaseModel)


def _ensure_list(d):
    """
    Helper function to ensure data is in list format when many=True.

    This handles TOML's structure where arrays might be nested in sections.
    """
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and len(d) == 1 and isinstance(next(iter(d.values())), list):
        return next(iter(d.values()))
    return [d]


class TomlAdapter(Adapter[T]):
    """
    Adapter for converting between Pydantic models and TOML data.

    This adapter handles TOML files and strings, providing methods to:
    - Parse TOML data into Pydantic model instances
    - Convert Pydantic models to TOML format
    - Handle both single objects and arrays of objects

    Attributes:
        obj_key: The key identifier for this adapter type ("toml")

    Example:
        ```python
        from pydantic import BaseModel
        from pydapter.adapters.toml_ import TomlAdapter

        class Person(BaseModel):
            name: str
            age: int

        # Parse TOML data
        toml_data = '''
        name = "John"
        age = 30
        '''
        person = TomlAdapter.from_obj(Person, toml_data)

        # Parse TOML array
        toml_array = '''
        [[people]]
        name = "John"
        age = 30

        [[people]]
        name = "Jane"
        age = 25
        '''
        people = TomlAdapter.from_obj(Person, toml_array, many=True)

        # Convert to TOML
        toml_output = TomlAdapter.to_obj(person)
        ```
    """

    obj_key = "toml"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | Path,
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
                    raise ParseError(f"Failed to read TOML file: {e}", source=str(obj))
            else:
                text = obj

            # Check for empty input
            if not text or (isinstance(text, str) and not text.strip()):
                raise ParseError(
                    "Empty TOML content",
                    source=str(obj)[:100] if isinstance(obj, str) else str(obj),
                )

            # Parse TOML
            try:
                parsed = toml.loads(text, **kw)
            except toml.TomlDecodeError as e:
                raise ParseError(
                    f"Invalid TOML: {e}",
                    source=str(text)[:100] if isinstance(text, str) else str(text),
                )

            # Validate against model
            try:
                if many:
                    return [
                        getattr(subj_cls, adapt_meth)(x, **(adapt_kw or {}))
                        for x in _ensure_list(parsed)
                    ]
                return getattr(subj_cls, adapt_meth)(parsed, **(adapt_kw or {}))
            except ValidationError as e:
                raise AdapterValidationError(
                    f"Validation error: {e}",
                    data=parsed,
                    errors=e.errors(),
                )

        except (ParseError, AdapterValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ParseError(
                f"Unexpected error parsing TOML: {e}",
                source=str(obj)[:100] if isinstance(obj, str) else str(obj),
            )

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
                return ""

            payload = (
                {"items": [getattr(i, adapt_meth)(**(adapt_kw or {})) for i in items]}
                if many
                else getattr(items[0], adapt_meth)(**(adapt_kw or {}))
            )
            return toml.dumps(payload, **kw)

        except Exception as e:
            # Wrap exceptions
            raise ParseError(f"Error generating TOML: {e}")
