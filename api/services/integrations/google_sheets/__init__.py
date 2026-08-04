from __future__ import annotations

from api.services.integrations.base import IntegrationPackageSpec
from api.services.integrations.registry import register_package

from .completion import run_completion
from .node import NODE
from .routes import router

PACKAGE = register_package(
    IntegrationPackageSpec(
        name="google_sheets",
        nodes=(NODE,),
        run_completion=run_completion,
        routers=(router,),
    )
)

__all__ = ["PACKAGE"]
