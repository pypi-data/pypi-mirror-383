# 0/__init__.py
"""
Zero directory configuration modules.

This package contains configuration modules for OpenFOAM 0 directory field files:
- p (pressure field)
- U (velocity field)
- f (force field)
- lambda (scalar field)
"""

from . import p_config
from . import U_config
from . import f_config
from . import lambda_config

__all__ = [
    'p_config',
    'U_config',
    'f_config',
    'lambda_config'
]
