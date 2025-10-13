"""
Application factory utilities for Sweet Potato services.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager

from fastapi import APIRouter, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import SpapsAuthMiddleware, build_spaps_auth_service
from .logging import configure_logging
from .middleware import RequestLoggingMiddleware
from .settings import BaseServiceSettings

MiddlewareSpec = tuple[type[BaseHTTPMiddleware], dict[str, Any]]


def create_app(
    *,
    settings_loader: Callable[[], BaseServiceSettings],
    api_router: APIRouter,
    additional_middlewares: Iterable[MiddlewareSpec] | None = None,
    enable_request_logging: bool = True,
    request_logger_name: str | None = None,
    enable_spaps_auth: bool | None = None,
    auth_exempt_paths: Iterable[str] | None = None,
) -> FastAPI:
    """
    Build a fully configured FastAPI application.

    Args:
        settings_loader: Callable that returns the service's settings instance.
        api_router: Root API router composed by the service.
        additional_middlewares: Optional sequence of ``(middleware_class, kwargs)``
            tuples to include after the shared middleware.
        enable_request_logging: Toggle shared request logging middleware.
        request_logger_name: Optional structlog logger name override.
        enable_spaps_auth: Force-enable/disable SPAPS auth middleware. ``None`` falls
            back to the value of ``settings.spaps_auth_enabled``.
        auth_exempt_paths: Additional paths to exempt from SPAPS auth enforcement.
    """

    settings = settings_loader()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.debug,
    )

    if enable_request_logging:
        logger_name = request_logger_name or f"{settings.logger_namespace}.request"
        app.add_middleware(RequestLoggingMiddleware, logger_name=logger_name)  # type: ignore[arg-type]

    for middleware_spec in additional_middlewares or []:
        middleware_cls, kwargs = middleware_spec
        app.add_middleware(middleware_cls, **kwargs)  # type: ignore[arg-type]

    use_spaps_auth = enable_spaps_auth
    if use_spaps_auth is None:
        use_spaps_auth = settings.spaps_auth_enabled

    lifespan_context: Callable[[FastAPI], AsyncContextManager[None]] | None = None
    if use_spaps_auth:
        auth_service = build_spaps_auth_service(settings)
        app.state.spaps_auth_service = auth_service
        exempt_paths = {"/health", "/docs", "/redoc"}
        if auth_exempt_paths:
            exempt_paths.update(auth_exempt_paths)
        app.add_middleware(
            SpapsAuthMiddleware,
            auth_service=auth_service,
            exempt_paths=exempt_paths,
        )  # type: ignore[arg-type]

        @asynccontextmanager
        async def _lifespan(app: FastAPI):  # pragma: no cover - lifecycle hooks
            try:
                yield
            finally:
                await auth_service.aclose()

        lifespan_context = _lifespan

    if lifespan_context is not None:
        app.router.lifespan_context = lifespan_context  # type: ignore[assignment]

    app.include_router(api_router)

    return app
