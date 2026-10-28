import json
import logging
import time
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("crypto_ai")


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(), format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )


async def log_request(request: Request, call_next):
    # Generate locally; do not trust arbitrary IDs or log query strings/secrets.
    request.state.request_id = uuid4().hex
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    logger.info(
        json.dumps(
            {
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response
