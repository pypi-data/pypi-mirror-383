"""
Router composition helpers.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

RouterMount = APIRouter | tuple[APIRouter, dict[str, Any]]


def build_base_router(*routers: RouterMount) -> APIRouter:
    """
    Compose a base API router from child routers.

    Each positional argument can be either an `APIRouter` (included with default
    options) or a tuple of `(router, include_kwargs)` mirroring FastAPI's
    `include_router` signature.
    """

    base = APIRouter()
    for mount in routers:
        if isinstance(mount, tuple):
            router, kwargs = mount
        else:
            router, kwargs = mount, {}
        base.include_router(router, **kwargs)
    return base
