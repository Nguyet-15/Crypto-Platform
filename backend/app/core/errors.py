from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.logging import logger


def error_response(request: Request, status: int, code: str, message: str):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
        headers={"X-Request-ID": request_id},
    )


async def http_error(request: Request, exc: HTTPException):
    response = error_response(request, exc.status_code, "http_error", str(exc.detail))
    if exc.headers:
        response.headers.update(exc.headers)
    return response


async def validation_error(request: Request, exc: RequestValidationError):
    return error_response(
        request, 422, "validation_error", "Invalid request parameters"
    )


async def unexpected_error(request: Request, exc: Exception):
    logger.error(
        "Unhandled error request_id=%s type=%s",
        getattr(request.state, "request_id", "unknown"),
        type(exc).__name__,
    )
    return error_response(request, 500, "internal_error", "Internal server error")
