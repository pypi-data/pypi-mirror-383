# system/__init__.py
"""
System directory configuration modules.

This package contains configuration modules for OpenFOAM system directory files:
- blockMeshDict
- controlDict
- fvSchemes
- fvOptions
- setFieldsDict
- decomposeParDict
- snappyHexMeshDict
"""

from . import block_mesh_config
from . import control_config
from . import fv_schemes_config
from . import fv_options_config
from . import set_fields_config
from . import decompose_par_config
from . import snappy_hex_mesh_config

__all__ = [
    'block_mesh_config',
    'control_config',
    'fv_schemes_config',
    'fv_options_config',
    'set_fields_config',
    'decompose_par_config',
    'snappy_hex_mesh_config'
]
