"""Exception hierarchy for Digikala SDK."""

from typing import Optional, Any


class DigikalaAPIError(Exception):
    """
    Base exception for all Digikala API errors.

    Attributes:
        message: Error message
        status_code: HTTP status code (if applicable)
        response: Raw response data (if applicable)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class BadRequestError(DigikalaAPIError):
    """
    Exception for 400 Bad Request errors.

    Raised when the request is malformed or contains invalid parameters.
    """
    pass


class UnauthorizedError(DigikalaAPIError):
    """
    Exception for 401 Unauthorized errors.

    Raised when authentication credentials are missing or invalid.
    """
    pass


class ForbiddenError(DigikalaAPIError):
    """
    Exception for 403 Forbidden errors.

    Raised when the authenticated user does not have permission.
    """
    pass


class NotFoundError(DigikalaAPIError):
    """
    Exception for 404 Not Found errors.

    Raised when the requested resource does not exist.
    """
    pass


class RateLimitError(DigikalaAPIError):
    """
    Exception for 429 Too Many Requests errors.

    Raised when the API rate limit has been exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response: Optional[Any] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class ServerError(DigikalaAPIError):
    """
    Exception for 5xx Server errors.

    Raised when the API server encounters an internal error.
    """
    pass


class TimeoutError(DigikalaAPIError):
    """
    Exception for request timeout errors.

    Raised when a request exceeds the configured timeout.
    """
    pass


class ConnectionError(DigikalaAPIError):
    """
    Exception for connection errors.

    Raised when unable to establish connection to the API.
    """
    pass


class ValidationError(DigikalaAPIError):
    """
    Exception for response validation errors.

    Raised when the API response cannot be parsed or validated.
    """
    pass


class APIStatusError(DigikalaAPIError):
    """
    Exception for non-200 API status codes in response body.

    Raised when the API returns a response with status field != 200,
    indicating the request failed at the application level.

    Example:
        Response: {"status": 404, "message": "Product not found"}
        Raises: APIStatusError with status_code=404
    """

    def __init__(
        self,
        message: str = "API returned non-200 status",
        status_code: Optional[int] = None,
        response: Optional[Any] = None
    ):
        super().__init__(message, status_code, response)

    @classmethod
    def from_response(cls, status: int, response: Optional[Any] = None) -> "APIStatusError":
        """
        Create APIStatusError from response status code.

        Args:
            status: The status code from API response
            response: Optional raw response data

        Returns:
            Appropriate APIStatusError subclass based on status code
        """
        error_messages = {
            400: "Bad Request - Invalid parameters",
            401: "Unauthorized - Invalid or missing API key",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource does not exist",
            429: "Rate Limit Exceeded",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }

        message = error_messages.get(status, f"Request failed with status {status}")
        return cls(message=message, status_code=status, response=response)


class CircuitBreakerOpenError(DigikalaAPIError):
    """
    Exception raised when circuit breaker is OPEN.

    Raised when the circuit breaker is in OPEN state and fails fast
    without attempting the request.

    Attributes:
        failure_count: Number of consecutive failures that triggered the circuit
        retry_after: Seconds until circuit attempts to recover (HALF_OPEN)
    """

    def __init__(
        self,
        message: str = "Circuit breaker is OPEN",
        failure_count: int = 0,
        retry_after: Optional[float] = None
    ):
        super().__init__(message, status_code=None, response=None)
        self.failure_count = failure_count
        self.retry_after = retry_after

    def __str__(self) -> str:
        msg = f"{self.message} (failures: {self.failure_count})"
        if self.retry_after:
            msg += f", retry after {self.retry_after:.1f}s"
        return msg