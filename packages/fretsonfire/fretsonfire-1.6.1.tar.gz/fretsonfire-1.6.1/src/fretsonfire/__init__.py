"""Frets on Fire game package."""

from importlib import import_module

try:
    __version__ = import_module(".Version", __name__).version()
except Exception:  # pragma: no cover - metadata only
    __version__ = "0.0.dev0"

__all__ = []
