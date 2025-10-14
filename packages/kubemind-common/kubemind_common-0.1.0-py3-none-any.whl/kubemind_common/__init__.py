"""KubeMind shared package (kubemind_common)."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__version__ = "0.1.0"

if TYPE_CHECKING:
    from . import (
        api,
        cache,
        celery,
        config,
        contracts,
        db,
        errors,
        flags,
        http,
        jobs,
        k8s,
        logging,
        metrics,
        middleware,
        otel,
        redis,
        resilience,
        security,
        testing,
        utils,
        webhooks,
    )

# Lazily expose curated submodules so consumers can rely on stable imports.
__all__ = [
    "api",
    "cache",
    "celery",
    "config",
    "contracts",
    "db",
    "errors",
    "flags",
    "http",
    "jobs",
    "k8s",
    "logging",
    "metrics",
    "middleware",
    "otel",
    "redis",
    "resilience",
    "security",
    "testing",
    "utils",
    "webhooks",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
