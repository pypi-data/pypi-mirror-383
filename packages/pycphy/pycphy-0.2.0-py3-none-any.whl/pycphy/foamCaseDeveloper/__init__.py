"""
foamCaseDeveloper - OpenFOAM Case Development Tools

This module provides tools for creating and managing OpenFOAM simulation cases,
including mesh generation, control dictionary setup, and turbulence properties
configuration.

Author: Sanjeev Bashyal
"""

from .core import (
    BlockMeshDeveloper,
    CADBlockMeshDeveloper,
    FoamCaseManager
)
from .writers import (
    FoamWriter,
    BlockMeshWriter,
    ControlDictWriter,
    TurbulencePropertiesWriter,
    DynamicMeshDictWriter,
    HFDIBDEMDictWriter
)
from .config import (
    global_config,
    block_mesh_config,
    control_config,
    turbulence_config,
    dynamic_mesh_config,
    config_hfdibdem,
    cad_mesh_config
)
from ..config_manager import ConfigManager, create_config_from_template

__version__ = "0.1.0"

__all__ = [
    # Core functionality
    "BlockMeshDeveloper",
    "CADBlockMeshDeveloper",
    "FoamCaseManager",
    # Writers
    "FoamWriter",
    "BlockMeshWriter",
    "ControlDictWriter",
    "TurbulencePropertiesWriter",
    "DynamicMeshDictWriter",
    "HFDIBDEMDictWriter",
    # Configuration
    "global_config",
    "block_mesh_config",
    "control_config", 
    "turbulence_config",
    "dynamic_mesh_config",
    "config_hfdibdem",
    "cad_mesh_config",
    # Config manager utilities
    "ConfigManager",
    "create_config_from_template",
]
