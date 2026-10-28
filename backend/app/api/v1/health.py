import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import error_response
from app.db.session import check_database

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "crypto-ai-api", "version": "0.1.0"}


def get_database_check() -> Callable[[], None]:
    return check_database


@router.get("/ready", responses={503: {"description": "Database unavailable"}})
def readiness(
    request: Request, check: Annotated[Callable[[], None], Depends(get_database_check)]
):
    try:
        check()
    except SQLAlchemyError:
        logging.getLogger("crypto_ai").warning("Database readiness failed")
        return error_response(
            request, 503, "database_unavailable", "Database unavailable"
        )
    return {"status": "ready", "database": "ok"}
