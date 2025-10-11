"""
Extract Monster Python SDK Client
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import httpx

if TYPE_CHECKING:
    from pydantic import BaseModel
else:
    try:
        from pydantic import BaseModel
    except ImportError:
        BaseModel = None  # type: ignore[assignment, misc]

from extract_monster.exceptions import (
    APIError,
    AuthenticationError,
    QuotaExceededError,
    ValidationError,
)
from extract_monster.models import ExtractionResponse
from extract_monster.schemas import SchemaConverter


class ExtractMonster:
    """
    Extract Monster API client

    Examples:
        >>> from extract_monster import ExtractMonster
        >>> client = ExtractMonster(api_key="your_api_key")
        >>>
        >>> # Extract from file
        >>> result = client.extract_file("invoice.pdf", schema=InvoiceSchema)
        >>> print(result.extracted_data)
        >>>
        >>> # Extract from text
        >>> result = client.extract_text("John Doe, 555-1234", schema=ContactSchema)
        >>> print(result.extracted_data)
    """

    DEFAULT_BASE_URL = "https://api.extract.monster"
    DEFAULT_TIMEOUT = 300.0  # 5 minutes for file processing

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Extract Monster client

        Args:
            api_key: API key for authentication. If not provided, will look for
                    EXTRACT_MONSTER_API_KEY environment variable
            base_url: Base URL for API. Defaults to https://api.extract.monster
            timeout: Request timeout in seconds. Defaults to 300

        Raises:
            AuthenticationError: If no API key is provided or found
        """
        self.api_key = api_key or os.getenv("EXTRACT_MONSTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or "
                "EXTRACT_MONSTER_API_KEY environment variable"
            )

        self.base_url = (
            base_url or os.getenv("EXTRACT_MONSTER_BASE_URL") or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout

        # Create HTTP client
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )

    def _handle_response(self, response: httpx.Response) -> ExtractionResponse:
        """
        Handle API response and raise appropriate exceptions

        Args:
            response: HTTP response from API

        Returns:
            ExtractionResponse object

        Raises:
            AuthenticationError: If authentication fails
            QuotaExceededError: If quota is exceeded
            ValidationError: If validation fails
            APIError: For other API errors
        """
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code == 401:
            raise AuthenticationError(data.get("detail", "Authentication failed"))
        elif response.status_code == 429:
            raise QuotaExceededError(data.get("detail", "Usage quota exceeded"))
        elif response.status_code == 400:
            raise ValidationError(data.get("detail", "Validation failed"))
        elif response.status_code >= 400:
            raise APIError(
                data.get("detail", f"API error: {response.status_code}"),
                status_code=response.status_code,
            )

        return ExtractionResponse(
            status=data.get("status", "success"),
            extracted_data=data.get("extracted_data", {}),
            filename=data.get("filename"),
            file_type=data.get("file_type"),
            text_length=data.get("text_length"),
        )

    def extract_file(
        self,
        file_path: Union[str, Path],
        schema: Optional[Union[type[BaseModel], dict[str, Any]]] = None,
    ) -> ExtractionResponse:
        """
        Extract structured data from a file

        Args:
            file_path: Path to file to extract data from
            schema: Optional schema as Pydantic model class or dict

        Returns:
            ExtractionResponse containing extracted data

        Raises:
            FileNotFoundError: If file doesn't exist
            AuthenticationError: If authentication fails
            QuotaExceededError: If quota is exceeded
            ValidationError: If validation fails
            APIError: For other API errors

        Examples:
            >>> # With Pydantic model
            >>> from pydantic import BaseModel
            >>>
            >>> class Invoice(BaseModel):
            ...     invoice_number: str
            ...     total: float
            >>>
            >>> result = client.extract_file("invoice.pdf", schema=Invoice)
            >>>
            >>> # With dict schema
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {
            ...         "invoice_number": {"type": "string"},
            ...         "total": {"type": "number"}
            ...     }
            ... }
            >>> result = client.extract_file("invoice.pdf", schema=schema)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Convert schema to JSON string
        schema_str = SchemaConverter.convert_schema(schema)

        # Prepare request
        url = f"{self.base_url}/v1/extract/file"

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            data = {}
            if schema_str:
                data["schema"] = schema_str

            response = self._client.post(url, files=files, data=data)

        return self._handle_response(response)

    def extract_text(
        self,
        text: str,
        schema: Optional[Union[type[BaseModel], dict[str, Any]]] = None,
    ) -> ExtractionResponse:
        """
        Extract structured data from text

        Args:
            text: Text content to extract data from
            schema: Optional schema as Pydantic model class or dict

        Returns:
            ExtractionResponse containing extracted data

        Raises:
            ValidationError: If text is empty or validation fails
            AuthenticationError: If authentication fails
            QuotaExceededError: If quota is exceeded
            APIError: For other API errors

        Examples:
            >>> # With Pydantic model
            >>> from pydantic import BaseModel
            >>>
            >>> class Contact(BaseModel):
            ...     name: str
            ...     phone: str
            >>>
            >>> result = client.extract_text("John Doe, 555-1234", schema=Contact)
            >>>
            >>> # Without schema (freeform extraction)
            >>> result = client.extract_text("Extract key information from this text")
        """
        if not text or not text.strip():
            raise ValidationError("Text content is required and cannot be empty")

        # Convert schema to JSON string
        schema_str = SchemaConverter.convert_schema(schema)

        # Prepare request
        url = f"{self.base_url}/v1/extract/text"
        data = {"text": text}
        if schema_str:
            data["schema"] = schema_str

        response = self._client.post(url, data=data)

        return self._handle_response(response)

    def close(self):
        """Close HTTP client"""
        self._client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
