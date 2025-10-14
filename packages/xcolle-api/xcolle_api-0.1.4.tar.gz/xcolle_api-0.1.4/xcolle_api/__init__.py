import importlib.metadata

__version__ = importlib.metadata.version("xcolle-api")

from .gcolle import GcolleAPI
from .pcolle import PcolleAPI

__all__ = ["GcolleAPI", "PcolleAPI"]
