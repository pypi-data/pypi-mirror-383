from . import performance
from . import plotting
from . import tears
from . import utils

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = ['performance', 'plotting', 'tears', 'utils', '__version__']