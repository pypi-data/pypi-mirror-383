"""Civic Transparency CWE types package.

Toolkit for CWE operations, standards processing, batch operations,
and validation workflows. Provides immutable result types, rich error handling,
and functional operations across all transparency-related domains.

"""

from importlib import metadata as _md

try:
    __version__: str = _md.version("civic-transparency-py-cwe-types")
except _md.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__"]
