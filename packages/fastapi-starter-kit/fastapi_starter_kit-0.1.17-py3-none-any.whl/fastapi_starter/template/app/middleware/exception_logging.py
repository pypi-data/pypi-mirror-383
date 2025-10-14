"""
exception_logging.py - Middleware to log unhandled exceptions.

This middleware intercepts all requests, logs any unhandled exceptions,
and returns a standardized JSON response with status code 500.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger

# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------
logger = get_logger(__name__)


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log unhandled exceptions during request processing.

    Usage:
        Add this middleware to your FastAPI app:
            app.add_middleware(ExceptionLoggingMiddleware)
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the incoming request, catch unhandled exceptions, log them,
        and return a standardized JSON error response.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable): The next middleware or route handler.

        Returns:
            Response: Normal response if no exception, or JSON error response if exception occurs.
        """
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log exception with traceback
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            # Return standardized 500 response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
