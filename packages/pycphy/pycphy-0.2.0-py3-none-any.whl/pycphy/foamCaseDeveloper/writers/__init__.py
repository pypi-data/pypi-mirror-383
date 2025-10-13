"""
OpenFOAM dictionary writers for various file types.

This module contains the base FoamWriter class and specific writers
for different OpenFOAM dictionary files.
"""

from .foam_writer import FoamWriter

# Import writers from subdirectories
from .constant.turbulence_properties_writer import TurbulencePropertiesWriter
from .constant.transport_properties_writer import TransportPropertiesWriter
from .constant.dynamic_mesh_dict_writer import DynamicMeshDictWriter
from .constant.gravity_field_writer import GravityFieldWriter
from .constant.hfdibdem_dict_writer import HFDIBDEMDictWriter

from .system.block_mesh_writer import BlockMeshWriter
from .system.control_dict_writer import ControlDictWriter
from .system.fv_schemes_writer import FvSchemesWriter
from .system.fv_options_writer import FvOptionsWriter
from .system.set_fields_writer import SetFieldsWriter
from .system.decompose_par_writer import DecomposeParWriter
from .system.snappy_hex_mesh_writer import SnappyHexMeshWriter

from .zero.p_field_writer import PFieldWriter
from .zero.u_field_writer import UFieldWriter
from .zero.f_field_writer import FFieldWriter
from .zero.lambda_field_writer import LambdaFieldWriter

__all__ = [
    "FoamWriter",
    # Constant directory writers
    "TurbulencePropertiesWriter",
    "TransportPropertiesWriter",
    "DynamicMeshDictWriter",
    "GravityFieldWriter",
    "HFDIBDEMDictWriter",
    # System directory writers
    "BlockMeshWriter", 
    "ControlDictWriter",
    "FvSchemesWriter",
    "FvOptionsWriter",
    "SetFieldsWriter",
    "DecomposeParWriter",
    "SnappyHexMeshWriter",
    # Zero directory writers
    "PFieldWriter",
    "UFieldWriter",
    "FFieldWriter",
    "LambdaFieldWriter",
]
