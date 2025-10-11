"""
Custom exceptions for Extract Monster SDK
"""

from typing import Optional


class ExtractMonsterError(Exception):
    """Base exception for all Extract Monster errors"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(ExtractMonsterError):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class QuotaExceededError(ExtractMonsterError):
    """Raised when API quota is exceeded"""

    def __init__(self, message: str = "Usage quota exceeded"):
        super().__init__(message, status_code=429)


class ValidationError(ExtractMonsterError):
    """Raised when request validation fails"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class APIError(ExtractMonsterError):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code)
