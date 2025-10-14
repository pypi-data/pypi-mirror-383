from .core import VectorCache
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("vector-cache-memory")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["VectorCache"]