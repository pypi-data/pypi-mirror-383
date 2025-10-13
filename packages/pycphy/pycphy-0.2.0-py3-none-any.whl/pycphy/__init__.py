"""
pycphy package root exports.
"""

from .config_manager import ConfigManager, create_config_from_template  # re-export for convenience

__all__ = [
    "ConfigManager",
    "create_config_from_template",
]

"""
pycphy - Python: Computational Physics

A Python package for computational physics simulations and tools.

Author: Sanjeev Bashyal
Location: https://github.com/SanjeevBashyal/pycphy
"""

__version__ = "0.1.0"
__author__ = "Sanjeev Bashyal"
__email__ = "sanjeev.bashyal@example.com"
__url__ = "https://github.com/SanjeevBashyal/pycphy"

# Import main modules for easy access
from . import foamCaseDeveloper

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__url__",
    "foamCaseDeveloper",
]
