import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from instrava_api.core.config import settings
from instrava_api.core.exceptions import EmailAlreadyRegisteredError
from instrava_api.routers.auth import router as auth_router

logger = logging.getLogger("instrava_api")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Global Exception Handlers
    @application.exception_handler(EmailAlreadyRegisteredError)
    async def email_already_registered_handler(
        request: Request, exc: EmailAlreadyRegisteredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": {"code": exc.code, "message": exc.message}},
        )

    @application.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        if isinstance(exc, (HTTPException, RequestValidationError)):
            # Let FastAPI's default handlers deal with HTTP and validation exceptions
            raise exc
        logger.error("Internal server error: %s", type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Include routers
    application.include_router(auth_router, prefix=settings.API_V1_STR)

    @application.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
