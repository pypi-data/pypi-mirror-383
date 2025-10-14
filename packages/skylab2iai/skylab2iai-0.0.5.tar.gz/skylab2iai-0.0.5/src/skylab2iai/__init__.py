"""
Skylab2IAI - A Python library for accessing and analyzing Skylab mission data.
"""

__version__ = "0.0.4"

from .catalog.catalog import Skylab2iaiCatalog
from src.skylab2iai.storage.plate_frame import SkylabPlateFrameCatalog

__all__ = [
    "Skylab2iaiCatalog",
    "SkylabPlateFrameCatalog",
]
