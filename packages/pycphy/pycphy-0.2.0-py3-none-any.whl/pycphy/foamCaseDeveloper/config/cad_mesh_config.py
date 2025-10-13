"""
Configuration classes for CAD-based mesh generation.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BlockParameter:
    """Configuration for a single block in the mesh."""
    block_id: str
    cells_x: int
    cells_y: int
    cells_z: int
    grading: str
    description: Optional[str] = None


@dataclass
class PatchParameter:
    """Configuration for a patch boundary condition."""
    region_name: str
    patch_name: str
    patch_type: str


@dataclass
class CADMeshConfig:
    """Configuration for CAD-based mesh generation."""
    
    # File paths
    blocks_csv_file: str = "Inputs/blocks.csv"
    patches_csv_file: str = "Inputs/patches.csv"
    output_path: str = "system/blockMeshDict"
    
    # XData configuration
    block_xdata_app_name: str = "BLOCKDATA"
    region_xdata_app_name: str = "REGIONDATA"
    
    # Processing parameters
    tolerance: float = 1e-6
    
    # Mesh parameters
    scale: float = 1.0
    
    # Block parameters (can be loaded from CSV or set directly)
    block_parameters: Optional[Dict[str, BlockParameter]] = None
    
    # Patch parameters (can be loaded from CSV or set directly)
    patch_parameters: Optional[Dict[str, PatchParameter]] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.block_parameters is None:
            self.block_parameters = {}
        if self.patch_parameters is None:
            self.patch_parameters = {}


# Default configuration instance
default_cad_mesh_config = CADMeshConfig()
