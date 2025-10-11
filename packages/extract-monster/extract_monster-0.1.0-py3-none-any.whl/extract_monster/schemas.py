"""
Schema conversion utilities for Extract Monster SDK
"""

import json
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
else:
    try:
        from pydantic import BaseModel

        PYDANTIC_AVAILABLE = True
    except ImportError:
        PYDANTIC_AVAILABLE = False
        BaseModel = None  # type: ignore[assignment, misc]


class SchemaConverter:
    """Convert between Pydantic models and JSON schemas"""

    @staticmethod
    def is_pydantic_model(schema: Any) -> bool:
        """Check if schema is a Pydantic model class"""
        if not PYDANTIC_AVAILABLE or BaseModel is None:
            return False

        try:
            return isinstance(schema, type) and issubclass(schema, BaseModel)
        except TypeError:
            return False

    @staticmethod
    def pydantic_to_json_schema(model: type[BaseModel]) -> dict[str, Any]:
        """
        Convert Pydantic model to JSON schema

        Args:
            model: Pydantic model class

        Returns:
            JSON schema dictionary
        """
        if not PYDANTIC_AVAILABLE:
            raise ImportError(
                "Pydantic is required to use Pydantic models. "
                "Install it with: pip install pydantic"
            )

        # Use Pydantic's built-in schema generation
        # For Pydantic v2
        if hasattr(model, "model_json_schema"):
            return model.model_json_schema()
        # For Pydantic v1
        elif hasattr(model, "schema"):
            return model.schema()
        else:
            raise ValueError("Unable to generate JSON schema from Pydantic model")

    @staticmethod
    def convert_schema(schema: Union[type[BaseModel], dict[str, Any], None]) -> Union[str, None]:
        """
        Convert schema to JSON string format expected by API

        Args:
            schema: Pydantic model class, dict, or None

        Returns:
            JSON string or None
        """
        if schema is None:
            return None

        # If it's a Pydantic model, convert to JSON schema
        if SchemaConverter.is_pydantic_model(schema):
            json_schema = SchemaConverter.pydantic_to_json_schema(schema)  # type: ignore[arg-type]
            return json.dumps(json_schema)

        # If it's a dict, convert to JSON string
        if isinstance(schema, dict):
            return json.dumps(schema)

        # If it's already a string, return as is
        if isinstance(schema, str):
            return schema

        raise ValueError(
            f"Schema must be a Pydantic model class, dict, or None. Got: {type(schema)}"
        )
