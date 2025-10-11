"""Custom exceptions for urlops"""

from typing import Optional


class URLParseError(Exception):
    """Base exception for urlops errors"""

    pass


class ParseError(URLParseError):
    """Raised when URL parsing fails"""

    def __init__(
        self, message: str, url: Optional[str] = None, position: Optional[int] = None
    ):
        super().__init__(message)
        self.url = url
        self.position = position


class ValidationError(URLParseError):
    """Raised when URL validation fails"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field


class TypeError(URLParseError):
    """Raised when incorrect types are provided"""

    def __init__(
        self,
        message: str,
        expected_type: Optional[str] = None,
        actual_type: Optional[str] = None,
    ):
        super().__init__(message)
        self.expected_type = expected_type
        self.actual_type = actual_type
