"""
main.py - FastAPI application entry point.

Initializes the FastAPI app, configures middleware, exception handlers,
database connection, and router registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import get_logger
from app.middleware.exception_logging import ExceptionLoggingMiddleware
from app.routers import users

# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------
logger = get_logger(__name__)

# -------------------------------------------------------------------
# FastAPI app initialization
# -------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

# -------------------------------------------------------------------
# Register routers
# -------------------------------------------------------------------
account_routers = [
    users.user_router,
    # Add future routers here
]

for router in account_routers:
    app.include_router(router=router)

# -------------------------------------------------------------------
# Middleware configuration
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (adjust for production)
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
    allow_credentials=True,
)

# Custom middleware to log unhandled exceptions
app.add_middleware(ExceptionLoggingMiddleware)

# -------------------------------------------------------------------
# Exception handlers
# -------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all uncaught exceptions globally.

    Logs the full traceback to the application log and returns a
    generic 500 Internal Server Error response to the client.
    """
    logger.error(
        f"Unhandled exception at {request.url}",
        exc_info=exc
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(FastAPIValidationError)
async def validation_exception_handler(request: Request, exc: FastAPIValidationError):
    """
    Handle FastAPI validation errors (e.g., invalid request body or parameters).

    Logs detailed validation error information and returns a structured
    JSON response with validation details.
    """
    logger.warning(f"Validation error at {request.url}: {exc.errors()} | Body: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# -------------------------------------------------------------------
# Application lifespan (startup/shutdown)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle context manager for the FastAPI app.

    Creates database tables on startup and logs success or failure.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except ProgrammingError as exc:
        logger.error(f"Error creating tables: {exc}")
    yield


# Attach lifespan handler to the app
app.router.lifespan_context = lifespan

# -------------------------------------------------------------------
# Run the FastAPI app (development entry point)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
