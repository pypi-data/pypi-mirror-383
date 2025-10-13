"""Exceptions for CRL API SDK."""


class CRLAPIError(Exception):
    """Base exception for CRL API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(CRLAPIError):
    """Authentication failed (401)."""
    pass


class ValidationError(CRLAPIError):
    """Request validation failed (400)."""
    pass


class RateLimitError(CRLAPIError):
    """Rate limit exceeded (429)."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ConflictError(CRLAPIError):
    """Idempotency conflict or replay (409)."""
    pass


class NotFoundError(CRLAPIError):
    """Resource not found (404)."""
    pass


class ServerError(CRLAPIError):
    """Server error (5xx)."""
    pass
