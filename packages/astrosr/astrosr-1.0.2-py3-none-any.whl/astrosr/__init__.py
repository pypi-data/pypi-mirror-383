"""
astroSR: Astronomical super-resolution with drizzle.

This package provides tools for combining wide field-of-view astronomical
images using the drizzle algorithm for enhanced resolution and quality.
"""

from .drizzle_super_resolution import drizzle_super_resolution

__version__ = "1.0.0"
__author__ = "Gabriel Ferrer"
__email__ = "gabriel.ferrer@example.com"

__all__ = [
    "drizzle_super_resolution",
    "__version__",
]
