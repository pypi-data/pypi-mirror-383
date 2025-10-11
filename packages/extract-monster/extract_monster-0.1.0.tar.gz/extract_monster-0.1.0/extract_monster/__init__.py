"""
Extract Monster Python SDK

A Python client library for the Extract Monster API - Extract structured data
from files and text using AI.
"""

from extract_monster.client import ExtractMonster
from extract_monster.exceptions import (
    APIError,
    AuthenticationError,
    ExtractMonsterError,
    QuotaExceededError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "ExtractMonster",
    "ExtractMonsterError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "APIError",
]
