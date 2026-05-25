import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.config import settings
from app.logging import configure_logging, logger, request_id_var

# Initialize structured logging configuration
configure_logging(log_level=settings.LOG_LEVEL, app_env=settings.APP_ENV)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request lifecycles, inject Request IDs, and measure duration.

    Request IDs are automatically attached to all log statements created during
    the scope of the request and returned in the HTTP headers.
    """

    async def dispatch(self, request: Request, call_next):
        # 1. Extract or generate a Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # 2. Inject Request ID into thread-local/task-local ContextVar
        token = request_id_var.set(request_id)

        start_time = time.perf_counter()

        # Log request receipt
        logger.info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
        )

        try:
            # Execute the request chain
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            # Attach headers for tracing
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"

            # Log request termination status
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration=f"{process_time:.4f}s",
            )
            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception(
                "Unhandled exception occurred during request execution",
                duration=f"{process_time:.4f}s",
                error=str(e),
            )
            raise

        finally:
            # 3. Clean up ContextVar to prevent cross-contamination
            request_id_var.reset(token)


# Create FastAPI App Instance
app = FastAPI(
    title="Nayki Production Backend",
    description=(
        "Production-ready backend API foundation for Nayki, "
        "an Android-first safety-navigation app."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enforce standard CORS Policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Request ID tracing middleware
app.add_middleware(RequestTracingMiddleware)

# Mount central API routing
app.include_router(api_router)


@app.get("/", tags=["General"])
async def root() -> dict:
    """Home directory redirecting developers to API documentation."""
    return {
        "project": "Nayki Safety Navigation",
        "stage": "Part 1 Foundation Setup",
        "documentation_url": "/docs",
    }
