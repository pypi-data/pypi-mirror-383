"""pymetadata - Python utilities for metadata."""

from pathlib import Path

__author__ = "Matthias Koenig"
__version__ = "0.5.4"


program_name: str = "pymetadata"
RESOURCES_DIR: Path = Path(__file__).parent / "resources"
ENUM_DIR: Path = Path(__file__).parent / "metadata"

CACHE_USE: bool = False
CACHE_PATH: Path = Path.home() / ".cache" / "pymetadata"
