"""
Response models for Extract Monster SDK
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ExtractionResponse:
    """Response from an extraction operation"""

    status: str
    extracted_data: dict[str, Any]
    filename: Optional[str] = None
    file_type: Optional[str] = None
    text_length: Optional[int] = None

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to extracted_data"""
        return self.extracted_data[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from extracted_data with default"""
        return self.extracted_data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "status": self.status,
            "extracted_data": self.extracted_data,
            "filename": self.filename,
            "file_type": self.file_type,
            "text_length": self.text_length,
        }
