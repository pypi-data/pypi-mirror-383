"""
MathyKit - A lightweight AI framework for Meta models
"""

from .core import Model
from .models import MetaOPT
from .version import __version__

__all__ = ["Model", "MetaOPT", "__version__"]