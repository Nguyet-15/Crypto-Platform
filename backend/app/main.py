from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from app.api.v1.health import router as health_router
from app.api.v1.modules import router as modules_router
from app.core.config import settings
from app.core.errors import http_error, unexpected_error, validation_error
from app.core.logging import configure_logging, log_request
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    yield
    engine.dispose()


app = FastAPI(title="Crypto AI Research API", version="0.1.0", lifespan=lifespan)
app.middleware("http")(log_request)
app.add_exception_handler(HTTPException, http_error)
app.add_exception_handler(RequestValidationError, validation_error)
app.add_exception_handler(Exception, unexpected_error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(modules_router, prefix="/api/v1")
