"""
Configuration files for OpenFOAM case setup.

This module provides configuration files for different aspects of
OpenFOAM case setup, including geometry, control, and turbulence settings.
Each config file contains detailed comments explaining all parameters.

Usage:
    from pycphy.foamCaseDeveloper.config import global_config
    from pycphy.foamCaseDeveloper.config import block_mesh_config
    from pycphy.foamCaseDeveloper.config import control_config
    from pycphy.foamCaseDeveloper.config import turbulence_config
"""

# Import all config modules
from . import global_config
from . import config_hfdibdem
from . import cad_mesh_config
from . import csv_boundary_reader

# Import config modules from subdirectories
from .constant import (
    turbulence_config,
    transport_properties_config,
    dynamic_mesh_config,
    gravity_field_config
)

from .system import (
    block_mesh_config,
    control_config,
    fv_schemes_config,
    fv_options_config,
    set_fields_config,
    decompose_par_config,
    snappy_hex_mesh_config
)

from .zero import (
    p_config,
    U_config,
    f_config,
    lambda_config
)

__all__ = [
    "global_config",
    "config_hfdibdem",
    "cad_mesh_config",
    "csv_boundary_reader",
    # Zero directory configs
    "p_config",
    "U_config",
    "f_config",
    "lambda_config",
    # Constant directory configs
    "turbulence_config",
    "transport_properties_config",
    "dynamic_mesh_config",
    "gravity_field_config",
    # System directory configs
    "block_mesh_config", 
    "control_config",
    "fv_schemes_config",
    "fv_options_config",
    "set_fields_config",
    "decompose_par_config",
    "snappy_hex_mesh_config",
]
