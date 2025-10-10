"""
Custom exceptions for the FounderX-AI Orchestration SDK.

This module defines a hierarchy of exceptions for different error scenarios.
"""

from typing import Any, Dict, Optional


class OrchestrationError(Exception):
    """Base exception for all SDK errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(OrchestrationError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(OrchestrationError):
    """Raised when authorization fails (403)."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(OrchestrationError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ValidationError(OrchestrationError):
    """Raised when request validation fails (422)."""

    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class RateLimitError(OrchestrationError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ServerError(OrchestrationError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, **kwargs)


class NetworkError(OrchestrationError):
    """Raised when network/connection errors occur."""

    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, **kwargs)


class TimeoutError(OrchestrationError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, **kwargs)


class StreamError(OrchestrationError):
    """Raised when streaming fails."""

    def __init__(self, message: str = "Streaming error", **kwargs):
        super().__init__(message, **kwargs)


def handle_http_error(status_code: int, message: str, response: Optional[Dict[str, Any]] = None) -> OrchestrationError:
    """
    Create appropriate exception based on HTTP status code.

    Args:
        status_code: HTTP status code
        message: Error message
        response: Response data

    Returns:
        Appropriate exception instance
    """
    if status_code == 401:
        return AuthenticationError(message, response=response)
    elif status_code == 403:
        return AuthorizationError(message, response=response)
    elif status_code == 404:
        return NotFoundError(message, response=response)
    elif status_code == 422:
        return ValidationError(message, response=response)
    elif status_code == 429:
        retry_after = None
        if response and "retry_after" in response:
            retry_after = response["retry_after"]
        return RateLimitError(message, retry_after=retry_after, response=response)
    elif 500 <= status_code < 600:
        return ServerError(message, status_code=status_code, response=response)
    else:
        return OrchestrationError(message, status_code=status_code, response=response)
