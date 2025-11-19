"""Mesh wizard package."""

from importlib.metadata import version

__all__ = [
    "__version__",
]

try:
    __version__ = version("cf-frp-traefik-mesh-wizard")
except Exception:  # pragma: no cover
    __version__ = "0.0.0"
