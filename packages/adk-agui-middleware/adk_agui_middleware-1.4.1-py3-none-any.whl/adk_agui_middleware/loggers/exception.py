# Copyright (C) 2025 Trend Micro Inc. All rights reserved.
"""HTTP exception handling and error response utilities for AGUI middleware."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import HTTPException, Request, status

from ..data_model.error import ErrorModel
from ..loggers.record_request_log import record_request_error_log, record_request_log
from ..manager.queue import QueueManager
from .record_log import record_error_log


def create_common_http_exception(
    status_code: int,
    error_message: str,
    error_description: dict[str, Any],
) -> HTTPException:
    """Create a standardized HTTP exception with structured error details.

    Constructs an HTTPException with a consistent error format using the
    ErrorModel for structured error responses.

    Args:
        :param status_code: HTTP status code for the exception
        :param error_message: Primary error message
        :param error_description: Dictionary containing detailed error information

    Returns:
        HTTPException with structured error detail
    """
    return HTTPException(
        status_code=status_code,
        detail=ErrorModel(
            error=error_message,
            error_description=error_description,
            timestamp=int(time.time()),
        ).model_dump(),
    )


def create_internal_server_error_exception(
    error_description: dict[str, Any],
) -> HTTPException:
    """Create a 500 Internal Server Error exception with error details.

    Convenience function for creating internal server error responses
    with consistent formatting.

    Args:
        :param error_description: Dictionary containing error details

    Returns:
        HTTPException with 500 status code and error details
    """
    return create_common_http_exception(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal Server Error.",
        error_description,
    )


@asynccontextmanager
async def http_exception_handler(request: Request) -> AsyncGenerator[None, Any]:
    """Async context manager for HTTP request exception handling.

    Provides centralized exception handling for HTTP requests, logging all
    requests and errors while converting unhandled exceptions to proper
    HTTP error responses.

    Args:
        :param request: FastAPI/Starlette request object

    Yields:
        None - context for the wrapped operation

    Raises:
        HTTPException: For both handled HTTP exceptions and converted general exceptions
    """
    try:
        # Log the incoming request
        await record_request_log(request)
        yield
    except HTTPException as e:
        # Re-raise HTTP exceptions after logging
        await record_request_error_log(request, e)
        raise
    except Exception as e:
        # Convert general exceptions to HTTP 500 errors
        await record_request_error_log(request, e)
        raise create_internal_server_error_exception({"error_message": repr(e)}) from e


@asynccontextmanager
async def adk_event_exception_handler(
    queue_controller: QueueManager,
) -> AsyncGenerator[None, Any]:
    """Context manager for ADK event stream exception handling.

    Ensures that ADK event streams always signal termination to the downstream
    queue consumer, even when exceptions occur. Logs exceptions and forwards the
    termination sentinel to the queue in a finally block.

    Args:
        :param queue_controller: QueueManager to receive the termination sentinel

    Yields:
        None – wraps the block that produces ADK events
    """
    try:
        yield
    except Exception as e:
        record_error_log("ADK Event exception", e)
        raise
    finally:
        await queue_controller.put(None)


@asynccontextmanager
async def agui_event_exception_handler(
    queue_controller: QueueManager,
) -> AsyncGenerator[None, Any]:
    """Context manager for AGUI event stream exception handling.

    Ensures that AGUI event streams always signal termination to the downstream
    queue consumer, even when exceptions occur. Logs exceptions and forwards the
    termination sentinel to the queue in a finally block.

    Args:
        :param queue_controller: QueueManager to receive the termination sentinel

    Yields:
        None – wraps the block that produces AGUI events
    """
    try:
        yield
    except Exception as e:
        record_error_log("AGUI Event exception", e)
        raise
    finally:
        await queue_controller.put(None)
