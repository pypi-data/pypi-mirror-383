# case_builder.py

"""
Case builder module for OpenFOAM case creation.

This module provides a more modular approach to building OpenFOAM cases
with clear separation of concerns and better error handling.
"""

import os
from typing import Dict, Any
from abc import ABC, abstractmethod

from ..writers.system.block_mesh_writer import BlockMeshWriter
from ..writers.system.control_dict_writer import ControlDictWriter
from ..writers.system.fv_schemes_writer import FvSchemesWriter
from ..writers.system.fv_options_writer import FvOptionsWriter
from ..writers.system.set_fields_writer import SetFieldsWriter
from ..writers.system.decompose_par_writer import DecomposeParWriter
from ..writers.system.snappy_hex_mesh_writer import SnappyHexMeshWriter

from ..writers.constant.turbulence_properties_writer import TurbulencePropertiesWriter
from ..writers.constant.dynamic_mesh_dict_writer import DynamicMeshDictWriter
from ..writers.constant.hfdibdem_dict_writer import HFDIBDEMDictWriter
from ..writers.constant.transport_properties_writer import TransportPropertiesWriter
from ..writers.constant.gravity_field_writer import GravityFieldWriter

from ..writers.zero.p_field_writer import PFieldWriter
from ..writers.zero.u_field_writer import UFieldWriter
from ..writers.zero.f_field_writer import FFieldWriter
from ..writers.zero.lambda_field_writer import LambdaFieldWriter
from .block_mesh_developer import BlockMeshDeveloper


class CaseComponent(ABC):
    """
    Abstract base class for OpenFOAM case components.
    
    Each component represents a specific part of an OpenFOAM case
    (e.g., mesh, control, turbulence, etc.).
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the case component.
        
        Args:
            name (str): Name of the component.
            description (str): Description of the component.
        """
        self.name = name
        self.description = description
        self.is_configured = False
        self.is_required = True
    
    @abstractmethod
    def configure(self, **kwargs) -> bool:
        """
        Configure the component with the provided parameters.
        
        Args:
            **kwargs: Configuration parameters.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def build(self, case_dir: str) -> bool:
        """
        Build the component (create files, etc.).
        
        Args:
            case_dir (str): Path to the OpenFOAM case directory.
            
        Returns:
            bool: True if build successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the component configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the component.
        
        Returns:
            Dict containing status information.
        """
        return {
            "name": self.name,
            "description": self.description,
            "is_configured": self.is_configured,
            "is_required": self.is_required,
            "is_valid": self.validate() if self.is_configured else False
        }


class GeometryComponent(CaseComponent):
    """Component for handling geometry and mesh configuration."""
    
    def __init__(self):
        super().__init__("Geometry", "Mesh geometry and blockMeshDict configuration")
        self.geometry_config = {}
        self.developer = None
    
    def configure(self, p0: tuple, p1: tuple, cells: tuple, 
                  patch_names: Dict[str, str], scale: float = 1.0) -> bool:
        """
        Configure the geometry component.
        
        Args:
            p0 (tuple): Minimum corner coordinates (x0, y0, z0).
            p1 (tuple): Maximum corner coordinates (x1, y1, z1).
            cells (tuple): Number of cells in each direction (nx, ny, nz).
            patch_names (Dict): Mapping of face identifiers to custom names.
            scale (float): Scaling factor for the mesh.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        try:
            self.geometry_config = {
                'p0': p0,
                'p1': p1,
                'cells': cells,
                'patch_names': patch_names,
                'scale': scale
            }
            
            self.developer = BlockMeshDeveloper(
                p0=p0, p1=p1, cells=cells, 
                patch_names=patch_names, scale=scale
            )
            
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Error configuring geometry: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the blockMeshDict file."""
        if not self.is_configured:
            print("Error: Geometry not configured")
            return False
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            bmd_path = os.path.join(system_dir, "blockMeshDict")
            
            # Check if this is CAD-based geometry (developer is None but blockMeshDict exists)
            if self.developer is None:
                # For CAD-based generation, the blockMeshDict should already exist
                if os.path.exists(bmd_path):
                    print(f"Using existing blockMeshDict from CAD generation: {bmd_path}")
                    return True
                else:
                    print(f"Error: CAD-based geometry configured but blockMeshDict not found at {bmd_path}")
                    return False
            else:
                # Traditional geometry generation
                self.developer.create_blockmesh_dict(file_path=bmd_path)
                return True
            
        except Exception as e:
            print(f"Error building geometry: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the geometry configuration."""
        if not self.is_configured:
            return False
        
        # Check if this is CAD-based geometry (has CAD mesh summary)
        if 'total_blocks' in self.geometry_config and 'total_patches' in self.geometry_config:
            # CAD-based geometry validation
            total_blocks = self.geometry_config.get('total_blocks', 0)
            total_patches = self.geometry_config.get('total_patches', 0)
            total_vertices = self.geometry_config.get('total_vertices', 0)
            
            if total_blocks <= 0:
                print(f"Invalid CAD geometry: {total_blocks} blocks")
                return False
            
            if total_patches <= 0:
                print(f"Invalid CAD geometry: {total_patches} patches")
                return False
            
            if total_vertices <= 0:
                print(f"Invalid CAD geometry: {total_vertices} vertices")
                return False
            
            return True
        
        # Traditional geometry validation
        required_keys = ['p0', 'p1', 'cells', 'patch_names']
        for key in required_keys:
            if key not in self.geometry_config:
                print(f"Missing required geometry parameter: {key}")
                return False
        
        # Check coordinate validity
        p0, p1, cells = self.geometry_config['p0'], self.geometry_config['p1'], self.geometry_config['cells']
        
        for i, (coord0, coord1) in enumerate(zip(p0, p1)):
            if coord1 <= coord0:
                print(f"Invalid geometry: p1[{i}] ({coord1}) must be > p0[{i}] ({coord0})")
                return False
        
        for i, cell_count in enumerate(cells):
            if not isinstance(cell_count, int) or cell_count <= 0:
                print(f"Invalid cell count in dimension {i}: {cell_count}")
                return False
        
        return True


class ControlComponent(CaseComponent):
    """Component for handling control dictionary configuration."""
    
    def __init__(self):
        super().__init__("Control", "Solver control and time stepping configuration")
        self.control_params = {}
        self.writer = None
    
    def configure(self, control_params: Dict[str, Any]) -> bool:
        """
        Configure the control component.
        
        Args:
            control_params (Dict): Dictionary of control parameters.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        try:
            self.control_params = control_params.copy()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Error configuring control: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the controlDict file."""
        if not self.is_configured:
            print("Error: Control not configured")
            return False
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            cd_path = os.path.join(system_dir, "controlDict")
            self.writer = ControlDictWriter(file_path=cd_path, params=self.control_params)
            
            # Validate parameters before writing
            if not self.writer.validate_params():
                print("Warning: Control parameters validation failed, but proceeding anyway.")
            
            self.writer.write()
            return True
            
        except Exception as e:
            print(f"Error building control: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the control configuration."""
        if not self.is_configured:
            return False
        
        required_params = ['application', 'startFrom', 'stopAt']
        for param in required_params:
            if param not in self.control_params:
                print(f"Missing required control parameter: {param}")
                return False
        
        return True


class TurbulenceComponent(CaseComponent):
    """Component for handling turbulence model configuration."""
    
    def __init__(self):
        super().__init__("Turbulence", "Turbulence model and properties configuration")
        self.simulation_type = ""
        self.model_properties = {}
        self.writer = None
    
    def configure(self, simulation_type: str, model_properties: Dict[str, Any]) -> bool:
        """
        Configure the turbulence component.
        
        Args:
            simulation_type (str): Type of turbulence simulation.
            model_properties (Dict): Properties for the turbulence model.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        try:
            self.simulation_type = simulation_type
            self.model_properties = model_properties.copy()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Error configuring turbulence: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the turbulenceProperties file."""
        if not self.is_configured:
            print("Error: Turbulence not configured")
            return False
        
        try:
            constant_dir = os.path.join(case_dir, "constant")
            os.makedirs(constant_dir, exist_ok=True)
            
            tp_path = os.path.join(constant_dir, "turbulenceProperties")
            self.writer = TurbulencePropertiesWriter(
                file_path=tp_path,
                simulation_type=self.simulation_type,
                model_properties=self.model_properties
            )
            
            # Validate configuration before writing
            if not self.writer.validate_simulation_type():
                print("Warning: Simulation type validation failed, but proceeding anyway.")
            
            if not self.writer.validate_model_properties():
                print("Warning: Model properties validation failed, but proceeding anyway.")
            
            self.writer.write()
            return True
            
        except Exception as e:
            print(f"Error building turbulence: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the turbulence configuration."""
        if not self.is_configured:
            return False
        
        valid_types = ['RAS', 'LES', 'laminar']
        if self.simulation_type not in valid_types:
            print(f"Invalid simulation type: {self.simulation_type}")
            return False
        
        return True


class DynamicMeshComponent(CaseComponent):
    """Component for handling dynamic mesh configuration."""
    
    def __init__(self):
        super().__init__("DynamicMesh", "Dynamic mesh configuration")
        self.is_required = False  # Optional component
        self.write_dynamic_mesh_dict = False
        self.mesh_type = ""
        self.mesh_properties = {}
        self.writer = None
    
    def configure(self, write_dynamic_mesh_dict: bool, mesh_type: str, 
                  mesh_properties: Dict[str, Any]) -> bool:
        """
        Configure the dynamic mesh component.
        
        Args:
            write_dynamic_mesh_dict (bool): Whether to write dynamicMeshDict.
            mesh_type (str): Type of dynamic mesh.
            mesh_properties (Dict): Properties for the dynamic mesh.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        try:
            self.write_dynamic_mesh_dict = write_dynamic_mesh_dict
            self.mesh_type = mesh_type
            self.mesh_properties = mesh_properties.copy()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Error configuring dynamic mesh: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the dynamicMeshDict file (if enabled)."""
        if not self.is_configured:
            print("Error: Dynamic mesh not configured")
            return False
        
        if not self.write_dynamic_mesh_dict:
            print("Dynamic mesh dictionary creation skipped (write_dynamic_mesh_dict is False).")
            return True
        
        try:
            constant_dir = os.path.join(case_dir, "constant")
            os.makedirs(constant_dir, exist_ok=True)
            
            dmd_path = os.path.join(constant_dir, "dynamicMeshDict")
            self.writer = DynamicMeshDictWriter(
                file_path=dmd_path,
                properties=self.mesh_properties
            )
            self.writer.write()
            return True
            
        except Exception as e:
            print(f"Error building dynamic mesh: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the dynamic mesh configuration."""
        if not self.is_configured:
            return False
        
        if not self.write_dynamic_mesh_dict:
            return True  # Skip validation if not enabled
        
        valid_types = ['solidBodyMotion', 'multiBodyOverset', 'adaptiveRefinement', 'morphingMesh']
        if self.mesh_type not in valid_types:
            print(f"Invalid mesh type: {self.mesh_type}")
            return False
        
        return True


class HFDIBDEMComponent(CaseComponent):
    """Component for handling HFDIBDEM configuration."""
    
    def __init__(self):
        super().__init__("HFDIBDEM", "Immersed Boundary DEM configuration")
        self.is_required = False  # Optional component
        self.write_hfdibdem_dict = False
        self.hfdibdem_properties = {}
        self.writer = None
    
    def configure(self, write_hfdibdem_dict: bool, hfdibdem_properties: Dict[str, Any]) -> bool:
        """
        Configure the HFDIBDEM component.
        
        Args:
            write_hfdibdem_dict (bool): Whether to write HFDIBDEMDict.
            hfdibdem_properties (Dict): Properties for the HFDIBDEM configuration.
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        try:
            self.write_hfdibdem_dict = write_hfdibdem_dict
            self.hfdibdem_properties = hfdibdem_properties.copy()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Error configuring HFDIBDEM: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the HFDIBDEMDict file (if enabled)."""
        if not self.is_configured:
            print("Error: HFDIBDEM not configured")
            return False
        
        if not self.write_hfdibdem_dict:
            print("HFDIBDEM dictionary creation skipped (write_hfdibdem_dict is False).")
            return True
        
        try:
            constant_dir = os.path.join(case_dir, "constant")
            os.makedirs(constant_dir, exist_ok=True)
            
            hfdibdem_path = os.path.join(constant_dir, "HFDIBDEMDict")
            self.writer = HFDIBDEMDictWriter(
                file_path=hfdibdem_path,
                properties=self.hfdibdem_properties
            )
            self.writer.write()
            return True
            
        except Exception as e:
            print(f"Error building HFDIBDEM: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the HFDIBDEM configuration."""
        if not self.is_configured:
            return False
        
        if not self.write_hfdibdem_dict:
            return True  # Skip validation if not enabled
        
        # Basic validation for HFDIBDEM properties
        required_keys = ['bodyNames', 'DEM', 'virtualMesh']
        for key in required_keys:
            if key not in self.hfdibdem_properties:
                print(f"Missing required HFDIBDEM parameter: {key}")
                return False
        
        return True


class TransportPropertiesComponent(CaseComponent):
    """Component for handling transport properties configuration."""
    
    def __init__(self):
        super().__init__("TransportProperties", "Fluid transport properties configuration")
        self.is_required = False  # Optional component
        self.write_transport_properties = False
        self.transport_model = ""
        self.model_properties = {}
        self.thermal_properties = {}
        self.species_properties = {}
        self.advanced_properties = {}
        self.writer = None
    
    def configure(self, write_transport_properties: bool, transport_model: str,
                  model_properties: Dict[str, Any], thermal_properties: Dict[str, Any] = None,
                  species_properties: Dict[str, Any] = None, advanced_properties: Dict[str, Any] = None) -> bool:
        """Configure the transport properties component."""
        try:
            self.write_transport_properties = write_transport_properties
            self.transport_model = transport_model
            self.model_properties = model_properties.copy()
            self.thermal_properties = thermal_properties or {}
            self.species_properties = species_properties or {}
            self.advanced_properties = advanced_properties or {}
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring transport properties: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the transportProperties file (if enabled)."""
        if not self.is_configured or not self.write_transport_properties:
            return True
        
        try:
            constant_dir = os.path.join(case_dir, "constant")
            os.makedirs(constant_dir, exist_ok=True)
            
            tp_path = os.path.join(constant_dir, "transportProperties")
            self.writer = TransportPropertiesWriter(
                file_path=tp_path,
                transport_model=self.transport_model,
                model_properties=self.model_properties,
                thermal_properties=self.thermal_properties,
                species_properties=self.species_properties,
                advanced_properties=self.advanced_properties
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building transport properties: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the transport properties configuration."""
        if not self.is_configured or not self.write_transport_properties:
            return True
        valid_models = ['Newtonian', 'NonNewtonian', 'BirdCarreau', 'CrossPowerLaw',
                       'HerschelBulkley', 'PowerLaw', 'Casson', 'GeneralizedNewtonian']
        if self.transport_model not in valid_models:
            print(f"Invalid transport model: {self.transport_model}")
            return False
        return True


class FvSchemesComponent(CaseComponent):
    """Component for handling finite volume schemes configuration."""
    
    def __init__(self):
        super().__init__("FvSchemes", "Finite volume discretization schemes configuration")
        self.is_required = False
        self.write_fv_schemes = False
        self.ddt_schemes = {}
        self.grad_schemes = {}
        self.div_schemes = {}
        self.laplacian_schemes = {}
        self.interpolation_schemes = {}
        self.sn_grad_schemes = {}
        self.flux_required = {}
        self.writer = None
    
    def configure(self, write_fv_schemes: bool, ddt_schemes: Dict[str, Any],
                  grad_schemes: Dict[str, Any], div_schemes: Dict[str, Any],
                  laplacian_schemes: Dict[str, Any], interpolation_schemes: Dict[str, Any],
                  sn_grad_schemes: Dict[str, Any], flux_required: Dict[str, Any] = None) -> bool:
        """Configure the fvSchemes component."""
        try:
            self.write_fv_schemes = write_fv_schemes
            self.ddt_schemes = ddt_schemes.copy()
            self.grad_schemes = grad_schemes.copy()
            self.div_schemes = div_schemes.copy()
            self.laplacian_schemes = laplacian_schemes.copy()
            self.interpolation_schemes = interpolation_schemes.copy()
            self.sn_grad_schemes = sn_grad_schemes.copy()
            self.flux_required = flux_required or {}
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring fvSchemes: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the fvSchemes file (if enabled)."""
        if not self.is_configured or not self.write_fv_schemes:
            return True
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            fvs_path = os.path.join(system_dir, "fvSchemes")
            self.writer = FvSchemesWriter(
                file_path=fvs_path,
                ddt_schemes=self.ddt_schemes,
                grad_schemes=self.grad_schemes,
                div_schemes=self.div_schemes,
                laplacian_schemes=self.laplacian_schemes,
                interpolation_schemes=self.interpolation_schemes,
                sn_grad_schemes=self.sn_grad_schemes,
                flux_required=self.flux_required
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building fvSchemes: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the fvSchemes configuration."""
        return True


class FvOptionsComponent(CaseComponent):
    """Component for handling finite volume options configuration."""
    
    def __init__(self):
        super().__init__("FvOptions", "Finite volume source terms and constraints configuration")
        self.is_required = False
        self.write_fv_options = False
        self.momentum_sources = {}
        self.thermal_sources = {}
        self.species_sources = {}
        self.turbulence_sources = {}
        self.pressure_sources = {}
        self.volume_fraction_sources = {}
        self.advanced_sources = {}
        self.writer = None
    
    def configure(self, write_fv_options: bool, momentum_sources: Dict[str, Any] = None,
                  thermal_sources: Dict[str, Any] = None, species_sources: Dict[str, Any] = None,
                  turbulence_sources: Dict[str, Any] = None, pressure_sources: Dict[str, Any] = None,
                  volume_fraction_sources: Dict[str, Any] = None, advanced_sources: Dict[str, Any] = None) -> bool:
        """Configure the fvOptions component."""
        try:
            self.write_fv_options = write_fv_options
            self.momentum_sources = momentum_sources or {}
            self.thermal_sources = thermal_sources or {}
            self.species_sources = species_sources or {}
            self.turbulence_sources = turbulence_sources or {}
            self.pressure_sources = pressure_sources or {}
            self.volume_fraction_sources = volume_fraction_sources or {}
            self.advanced_sources = advanced_sources or {}
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring fvOptions: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the fvOptions file (if enabled)."""
        if not self.is_configured or not self.write_fv_options:
            return True
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            fvo_path = os.path.join(system_dir, "fvOptions")
            self.writer = FvOptionsWriter(
                file_path=fvo_path,
                momentum_sources=self.momentum_sources,
                thermal_sources=self.thermal_sources,
                species_sources=self.species_sources,
                turbulence_sources=self.turbulence_sources,
                pressure_sources=self.pressure_sources,
                volume_fraction_sources=self.volume_fraction_sources,
                advanced_sources=self.advanced_sources
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building fvOptions: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the fvOptions configuration."""
        return True


class GravityFieldComponent(CaseComponent):
    """Component for handling gravity field configuration."""
    
    def __init__(self):
        super().__init__("GravityField", "Gravity field configuration")
        self.is_required = False
        self.write_gravity_field = False
        self.gravity_value = (0, 0, -9.81)
        self.dimensions = [0, 1, -2, 0, 0, 0, 0]
        self.writer = None
    
    def configure(self, write_gravity_field: bool, gravity_value: tuple,
                  dimensions: list = None) -> bool:
        """Configure the gravity field component."""
        try:
            self.write_gravity_field = write_gravity_field
            self.gravity_value = gravity_value
            self.dimensions = dimensions or [0, 1, -2, 0, 0, 0, 0]
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring gravity field: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the gravity field file (if enabled)."""
        if not self.is_configured or not self.write_gravity_field:
            return True
        
        try:
            constant_dir = os.path.join(case_dir, "constant")
            os.makedirs(constant_dir, exist_ok=True)
            
            g_path = os.path.join(constant_dir, "g")
            self.writer = GravityFieldWriter(
                file_path=g_path,
                gravity_value=self.gravity_value,
                dimensions=self.dimensions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building gravity field: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the gravity field configuration."""
        if not self.is_configured or not self.write_gravity_field:
            return True
        if not isinstance(self.gravity_value, (tuple, list)) or len(self.gravity_value) != 3:
            print("Gravity value must be a tuple/list with 3 components")
            return False
        return True


class SetFieldsComponent(CaseComponent):
    """Component for handling setFields configuration."""
    
    def __init__(self):
        super().__init__("SetFields", "Field initialization configuration")
        self.is_required = False
        self.write_set_fields_dict = False
        self.default_field_values = {}
        self.regions = {}
        self.writer = None
    
    def configure(self, write_set_fields_dict: bool, default_field_values: Dict[str, Any] = None,
                  regions: Dict[str, Any] = None) -> bool:
        """Configure the setFields component."""
        try:
            self.write_set_fields_dict = write_set_fields_dict
            self.default_field_values = default_field_values or {}
            self.regions = regions or {}
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring setFields: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the setFieldsDict file (if enabled)."""
        if not self.is_configured or not self.write_set_fields_dict:
            return True
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            sf_path = os.path.join(system_dir, "setFieldsDict")
            self.writer = SetFieldsWriter(
                file_path=sf_path,
                default_field_values=self.default_field_values,
                regions=self.regions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building setFields: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the setFields configuration."""
        return True


class DecomposeParComponent(CaseComponent):
    """Component for handling decomposePar configuration."""
    
    def __init__(self):
        super().__init__("DecomposePar", "Parallel decomposition configuration")
        self.is_required = False
        self.write_decompose_par_dict = False
        self.number_of_subdomains = 1
        self.method = "scotch"
        self.coeffs = {}
        self.options = {}
        self.fields = []
        self.preserve_patches = []
        self.preserve_cell_zones = []
        self.preserve_face_zones = []
        self.preserve_point_zones = []
        self.writer = None
    
    def configure(self, write_decompose_par_dict: bool, number_of_subdomains: int,
                  method: str, coeffs: Dict[str, Any] = None, options: Dict[str, Any] = None,
                  fields: list = None, preserve_patches: list = None, preserve_cell_zones: list = None,
                  preserve_face_zones: list = None, preserve_point_zones: list = None) -> bool:
        """Configure the decomposePar component."""
        try:
            self.write_decompose_par_dict = write_decompose_par_dict
            self.number_of_subdomains = number_of_subdomains
            self.method = method
            self.coeffs = coeffs or {}
            self.options = options or {}
            self.fields = fields or []
            self.preserve_patches = preserve_patches or []
            self.preserve_cell_zones = preserve_cell_zones or []
            self.preserve_face_zones = preserve_face_zones or []
            self.preserve_point_zones = preserve_point_zones or []
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring decomposePar: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the decomposeParDict file (if enabled)."""
        if not self.is_configured or not self.write_decompose_par_dict:
            return True
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            dp_path = os.path.join(system_dir, "decomposeParDict")
            self.writer = DecomposeParWriter(
                file_path=dp_path,
                number_of_subdomains=self.number_of_subdomains,
                method=self.method,
                coeffs=self.coeffs,
                options=self.options,
                fields=self.fields,
                preserve_patches=self.preserve_patches,
                preserve_cell_zones=self.preserve_cell_zones,
                preserve_face_zones=self.preserve_face_zones,
                preserve_point_zones=self.preserve_point_zones
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building decomposePar: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the decomposePar configuration."""
        if not self.is_configured or not self.write_decompose_par_dict:
            return True
        valid_methods = ['simple', 'hierarchical', 'scotch', 'metis', 'manual',
                        'multiLevel', 'structured', 'kahip', 'ptscotch']
        if self.method not in valid_methods:
            print(f"Invalid decomposition method: {self.method}")
            return False
        if not isinstance(self.number_of_subdomains, int) or self.number_of_subdomains < 1:
            print("numberOfSubdomains must be a positive integer")
            return False
        return True


class SnappyHexMeshComponent(CaseComponent):
    """Component for handling snappyHexMesh configuration."""
    
    def __init__(self):
        super().__init__("SnappyHexMesh", "Complex geometry mesh generation configuration")
        self.is_required = False
        self.write_snappy_hex_mesh_dict = False
        self.geometry = {}
        self.castellated_mesh_controls = {}
        self.snap_controls = {}
        self.add_layers_controls = {}
        self.mesh_quality_controls = {}
        self.merged_patches = []
        self.write_flags = {}
        self.writer = None
    
    def configure(self, write_snappy_hex_mesh_dict: bool, geometry: Dict[str, Any],
                  castellated_mesh_controls: Dict[str, Any], snap_controls: Dict[str, Any],
                  add_layers_controls: Dict[str, Any] = None, mesh_quality_controls: Dict[str, Any] = None,
                  merged_patches: list = None, write_flags: Dict[str, Any] = None) -> bool:
        """Configure the snappyHexMesh component."""
        try:
            self.write_snappy_hex_mesh_dict = write_snappy_hex_mesh_dict
            self.geometry = geometry.copy()
            self.castellated_mesh_controls = castellated_mesh_controls.copy()
            self.snap_controls = snap_controls.copy()
            self.add_layers_controls = add_layers_controls or {}
            self.mesh_quality_controls = mesh_quality_controls or {}
            self.merged_patches = merged_patches or []
            self.write_flags = write_flags or {}
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring snappyHexMesh: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the snappyHexMeshDict file (if enabled)."""
        if not self.is_configured or not self.write_snappy_hex_mesh_dict:
            return True
        
        try:
            system_dir = os.path.join(case_dir, "system")
            os.makedirs(system_dir, exist_ok=True)
            
            shm_path = os.path.join(system_dir, "snappyHexMeshDict")
            self.writer = SnappyHexMeshWriter(
                file_path=shm_path,
                geometry=self.geometry,
                castellated_mesh_controls=self.castellated_mesh_controls,
                snap_controls=self.snap_controls,
                add_layers_controls=self.add_layers_controls,
                mesh_quality_controls=self.mesh_quality_controls,
                merged_patches=self.merged_patches,
                write_flags=self.write_flags
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building snappyHexMesh: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the snappyHexMesh configuration."""
        if not self.is_configured or not self.write_snappy_hex_mesh_dict:
            return True
        if not self.geometry:
            print("Geometry dictionary is required for snappyHexMesh")
            return False
        if not self.castellated_mesh_controls:
            print("Castellated mesh controls are required for snappyHexMesh")
            return False
        if not self.snap_controls:
            print("Snap controls are required for snappyHexMesh")
            return False
        return True


class PFieldComponent(CaseComponent):
    """Component for handling pressure field (p) configuration."""
    
    def __init__(self):
        super().__init__("PField", "Pressure field initialization")
        self.is_required = False
        self.write_p_field = False
        self.internal_pressure = 0.0
        self.boundary_conditions = {}
        self.ref_pressure_cell = 0
        self.ref_pressure_value = 0.0
        self.pressure_dimensions = [0, 2, -2, 0, 0, 0, 0]
        self.writer = None
    
    def configure(self, write_p_field: bool, internal_pressure: float,
                  boundary_conditions: Dict[str, Any], ref_pressure_cell: int = 0,
                  ref_pressure_value: float = 0.0, pressure_dimensions: list = None) -> bool:
        """Configure the pressure field component."""
        try:
            self.write_p_field = write_p_field
            self.internal_pressure = internal_pressure
            self.boundary_conditions = boundary_conditions.copy()
            self.ref_pressure_cell = ref_pressure_cell
            self.ref_pressure_value = ref_pressure_value
            if pressure_dimensions:
                self.pressure_dimensions = pressure_dimensions
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring pressure field: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the pressure field file (if enabled)."""
        if not self.is_configured or not self.write_p_field:
            return True
        
        try:
            zero_dir = os.path.join(case_dir, "0")
            os.makedirs(zero_dir, exist_ok=True)
            
            p_path = os.path.join(zero_dir, "p")
            self.writer = PFieldWriter(
                file_path=p_path,
                internal_pressure=self.internal_pressure,
                boundary_conditions=self.boundary_conditions,
                ref_pressure_cell=self.ref_pressure_cell,
                ref_pressure_value=self.ref_pressure_value,
                pressure_dimensions=self.pressure_dimensions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building pressure field: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the pressure field configuration."""
        if not self.is_configured or not self.write_p_field:
            return True
        return True


class UFieldComponent(CaseComponent):
    """Component for handling velocity field (U) configuration."""
    
    def __init__(self):
        super().__init__("UField", "Velocity field initialization")
        self.is_required = False
        self.write_u_field = False
        self.internal_velocity = (0.0, 0.0, 0.0)
        self.boundary_conditions = {}
        self.velocity_dimensions = [0, 1, -1, 0, 0, 0, 0]
        self.writer = None
    
    def configure(self, write_u_field: bool, internal_velocity: tuple,
                  boundary_conditions: Dict[str, Any], velocity_dimensions: list = None) -> bool:
        """Configure the velocity field component."""
        try:
            self.write_u_field = write_u_field
            self.internal_velocity = internal_velocity
            self.boundary_conditions = boundary_conditions.copy()
            if velocity_dimensions:
                self.velocity_dimensions = velocity_dimensions
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring velocity field: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the velocity field file (if enabled)."""
        if not self.is_configured or not self.write_u_field:
            return True
        
        try:
            zero_dir = os.path.join(case_dir, "0")
            os.makedirs(zero_dir, exist_ok=True)
            
            u_path = os.path.join(zero_dir, "U")
            self.writer = UFieldWriter(
                file_path=u_path,
                internal_velocity=self.internal_velocity,
                boundary_conditions=self.boundary_conditions,
                velocity_dimensions=self.velocity_dimensions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building velocity field: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the velocity field configuration."""
        if not self.is_configured or not self.write_u_field:
            return True
        return True


class FFieldComponent(CaseComponent):
    """Component for handling force field (f) configuration."""
    
    def __init__(self):
        super().__init__("FField", "Force field initialization")
        self.is_required = False
        self.write_f_field = False
        self.internal_force = (0.0, 0.0, 0.0)
        self.boundary_conditions = {}
        self.force_dimensions = [0, 1, -2, 0, 0, 0, 0]
        self.writer = None
    
    def configure(self, write_f_field: bool, internal_force: tuple,
                  boundary_conditions: Dict[str, Any], force_dimensions: list = None) -> bool:
        """Configure the force field component."""
        try:
            self.write_f_field = write_f_field
            self.internal_force = internal_force
            self.boundary_conditions = boundary_conditions.copy()
            if force_dimensions:
                self.force_dimensions = force_dimensions
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring force field: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the force field file (if enabled)."""
        if not self.is_configured or not self.write_f_field:
            return True
        
        try:
            zero_dir = os.path.join(case_dir, "0")
            os.makedirs(zero_dir, exist_ok=True)
            
            f_path = os.path.join(zero_dir, "f")
            self.writer = FFieldWriter(
                file_path=f_path,
                internal_force=self.internal_force,
                boundary_conditions=self.boundary_conditions,
                force_dimensions=self.force_dimensions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building force field: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the force field configuration."""
        if not self.is_configured or not self.write_f_field:
            return True
        return True


class LambdaFieldComponent(CaseComponent):
    """Component for handling lambda field (λ) configuration."""
    
    def __init__(self):
        super().__init__("LambdaField", "Lambda field initialization")
        self.is_required = False
        self.write_lambda_field = False
        self.internal_lambda = 0.0
        self.boundary_conditions = {}
        self.lambda_dimensions = [0, 0, 0, 0, 0, 0, 0]
        self.writer = None
    
    def configure(self, write_lambda_field: bool, internal_lambda: float,
                  boundary_conditions: Dict[str, Any], lambda_dimensions: list = None) -> bool:
        """Configure the lambda field component."""
        try:
            self.write_lambda_field = write_lambda_field
            self.internal_lambda = internal_lambda
            self.boundary_conditions = boundary_conditions.copy()
            if lambda_dimensions:
                self.lambda_dimensions = lambda_dimensions
            self.is_configured = True
            return True
        except Exception as e:
            print(f"Error configuring lambda field: {e}")
            return False
    
    def build(self, case_dir: str) -> bool:
        """Build the lambda field file (if enabled)."""
        if not self.is_configured or not self.write_lambda_field:
            return True
        
        try:
            zero_dir = os.path.join(case_dir, "0")
            os.makedirs(zero_dir, exist_ok=True)
            
            lambda_path = os.path.join(zero_dir, "lambda")
            self.writer = LambdaFieldWriter(
                file_path=lambda_path,
                internal_lambda=self.internal_lambda,
                boundary_conditions=self.boundary_conditions,
                lambda_dimensions=self.lambda_dimensions
            )
            self.writer.write()
            return True
        except Exception as e:
            print(f"Error building lambda field: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate the lambda field configuration."""
        if not self.is_configured or not self.write_lambda_field:
            return True
        return True
