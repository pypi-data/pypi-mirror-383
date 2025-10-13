# foam_case_manager.py

import os
from typing import Dict, Any
from .case_builder import (
    GeometryComponent,
    ControlComponent,
    TurbulenceComponent,
    DynamicMeshComponent,
    HFDIBDEMComponent,
    TransportPropertiesComponent,
    FvSchemesComponent,
    FvOptionsComponent,
    GravityFieldComponent,
    SetFieldsComponent,
    DecomposeParComponent,
    SnappyHexMeshComponent,
    PFieldComponent,
    UFieldComponent,
    FFieldComponent,
    LambdaFieldComponent
)

class FoamCaseManager:
    """
    A comprehensive manager for creating and setting up OpenFOAM cases.
    
    This class provides a high-level interface for creating complete OpenFOAM
    case directories with all necessary configuration files using a modular
    component-based approach.
    """
    
    def __init__(self, case_name: str):
        """
        Initialize the FoamCaseManager.
        
        Args:
            case_name (str): The name of the OpenFOAM case directory.
        """
        self.case_name = case_name
        self.system_dir = os.path.join(case_name, "system")
        self.constant_dir = os.path.join(case_name, "constant")
        
        # Initialize components
        self.geometry = GeometryComponent()
        self.control = ControlComponent()
        self.turbulence = TurbulenceComponent()
        self.dynamic_mesh = DynamicMeshComponent()
        self.hfdibdem = HFDIBDEMComponent()
        self.transport_properties = TransportPropertiesComponent()
        self.fv_schemes = FvSchemesComponent()
        self.fv_options = FvOptionsComponent()
        self.gravity_field = GravityFieldComponent()
        self.set_fields = SetFieldsComponent()
        self.decompose_par = DecomposeParComponent()
        self.snappy_hex_mesh = SnappyHexMeshComponent()
        self.p_field = PFieldComponent()
        self.u_field = UFieldComponent()
        self.f_field = FFieldComponent()
        self.lambda_field = LambdaFieldComponent()
        
        # List of all components for easy iteration
        self.components = [
            self.geometry,
            self.control,
            self.turbulence,
            self.dynamic_mesh,
            self.hfdibdem,
            self.transport_properties,
            self.fv_schemes,
            self.fv_options,
            self.gravity_field,
            self.set_fields,
            self.decompose_par,
            self.snappy_hex_mesh,
            self.p_field,
            self.u_field,
            self.f_field,
            self.lambda_field
        ]
        
        # Ensure directories exist
        os.makedirs(self.system_dir, exist_ok=True)
        os.makedirs(self.constant_dir, exist_ok=True)
    
    def setup_geometry(self, p0: tuple, p1: tuple, cells: tuple, 
                      patch_names: Dict[str, str], scale: float = 1.0) -> bool:
        """
        Set up the geometry and mesh configuration.
        
        Args:
            p0 (tuple): The minimum corner of the cube (x0, y0, z0).
            p1 (tuple): The maximum corner of the cube (x1, y1, z1).
            cells (tuple): Number of cells in each direction (nx, ny, nz).
            patch_names (Dict): A dictionary mapping face identifiers to custom names.
            scale (float): The scaling factor for the mesh.
            
        Returns:
            bool: True if setup successful, False otherwise.
        """
        return self.geometry.configure(p0=p0, p1=p1, cells=cells, 
                                     patch_names=patch_names, scale=scale)
    
    def mark_geometry_ready(self, mesh_summary: Dict[str, Any] = None) -> bool:
        """
        Mark the geometry as configured when using CAD-based or external mesh generation.
        
        Args:
            mesh_summary (Dict): Optional summary of mesh information
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Mark geometry as configured
            self.geometry.is_configured = True
            
            # Store mesh summary if provided
            if mesh_summary:
                self.geometry.geometry_config = mesh_summary
            
            return True
        except Exception as e:
            print(f"Error marking geometry as ready: {e}")
            return False
    
    def setup_control(self, control_params: Dict[str, Any]) -> bool:
        """
        Set up the control dictionary parameters.
        
        Args:
            control_params (Dict): Dictionary containing control parameters.
            
        Returns:
            bool: True if setup successful, False otherwise.
        """
        return self.control.configure(control_params=control_params)
    
    def setup_turbulence(self, simulation_type: str, model_properties: Dict[str, Any]) -> bool:
        """
        Set up the turbulence model configuration.
        
        Args:
            simulation_type (str): The simulation type ('RAS', 'LES', 'laminar').
            model_properties (Dict): Properties for the turbulence model.
            
        Returns:
            bool: True if setup successful, False otherwise.
        """
        return self.turbulence.configure(simulation_type=simulation_type, 
                                       model_properties=model_properties)
    
    def setup_dynamic_mesh(self, write_dynamic_mesh_dict: bool, mesh_type: str, 
                          mesh_properties: Dict[str, Any]) -> bool:
        """
        Set up the dynamic mesh configuration.
        
        Args:
            write_dynamic_mesh_dict (bool): Whether to write dynamicMeshDict.
            mesh_type (str): The type of dynamic mesh ('solidBodyMotion', 'multiBodyOverset', etc.).
            mesh_properties (Dict): Properties for the dynamic mesh configuration.
            
        Returns:
            bool: True if setup successful, False otherwise.
        """
        return self.dynamic_mesh.configure(write_dynamic_mesh_dict=write_dynamic_mesh_dict,
                                         mesh_type=mesh_type, mesh_properties=mesh_properties)
    
    def setup_hfdibdem(self, write_hfdibdem_dict: bool, 
                      hfdibdem_properties: Dict[str, Any]) -> bool:
        """
        Set up the HFDIBDEM configuration.
        
        Args:
            write_hfdibdem_dict (bool): Whether to write HFDIBDEMDict.
            hfdibdem_properties (Dict): Properties for the HFDIBDEM configuration.
            
        Returns:
            bool: True if setup successful, False otherwise.
        """
        return self.hfdibdem.configure(write_hfdibdem_dict=write_hfdibdem_dict,
                                     hfdibdem_properties=hfdibdem_properties)
    
    def validate_all_components(self) -> bool:
        """
        Validate all configured components.
        
        Returns:
            bool: True if all required components are valid, False otherwise.
        """
        all_valid = True
        
        for component in self.components:
            if component.is_required and component.is_configured:
                if not component.validate():
                    print(f"Validation failed for {component.name}")
                    all_valid = False
            elif component.is_required and not component.is_configured:
                print(f"Required component {component.name} is not configured")
                all_valid = False
        
        return all_valid
    
    def get_component_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all components.
        
        Returns:
            Dict containing status information for each component.
        """
        status = {}
        for component in self.components:
            status[component.name] = component.get_status()
        return status
    
    def print_component_status(self):
        """Print the status of all components."""
        print(f"\n=== Component Status for '{self.case_name}' ===")
        for component in self.components:
            status = component.get_status()
            status_icon = "✓" if status['is_valid'] else "✗" if status['is_configured'] else "-"
            required_icon = "!" if status['is_required'] else ""
            print(f"{status_icon}{required_icon} {component.name}: {component.description}")
            if component.is_configured:
                print(f"    Configured: {status['is_configured']}, Valid: {status['is_valid']}")
            else:
                print(f"    Configured: {status['is_configured']}")
        print("=" * 50)
    
    def setup_transport_properties(self, write_transport_properties: bool, transport_model: str,
                                   model_properties: Dict[str, Any], thermal_properties: Dict[str, Any] = None,
                                   species_properties: Dict[str, Any] = None, advanced_properties: Dict[str, Any] = None) -> bool:
        """Set up transport properties configuration."""
        return self.transport_properties.configure(
            write_transport_properties=write_transport_properties,
            transport_model=transport_model,
            model_properties=model_properties,
            thermal_properties=thermal_properties,
            species_properties=species_properties,
            advanced_properties=advanced_properties
        )
    
    def setup_fv_schemes(self, write_fv_schemes: bool, ddt_schemes: Dict[str, Any],
                         grad_schemes: Dict[str, Any], div_schemes: Dict[str, Any],
                         laplacian_schemes: Dict[str, Any], interpolation_schemes: Dict[str, Any],
                         sn_grad_schemes: Dict[str, Any], flux_required: Dict[str, Any] = None) -> bool:
        """Set up finite volume schemes configuration."""
        return self.fv_schemes.configure(
            write_fv_schemes=write_fv_schemes,
            ddt_schemes=ddt_schemes,
            grad_schemes=grad_schemes,
            div_schemes=div_schemes,
            laplacian_schemes=laplacian_schemes,
            interpolation_schemes=interpolation_schemes,
            sn_grad_schemes=sn_grad_schemes,
            flux_required=flux_required
        )
    
    def setup_fv_options(self, write_fv_options: bool, momentum_sources: Dict[str, Any] = None,
                         thermal_sources: Dict[str, Any] = None, species_sources: Dict[str, Any] = None,
                         turbulence_sources: Dict[str, Any] = None, pressure_sources: Dict[str, Any] = None,
                         volume_fraction_sources: Dict[str, Any] = None, advanced_sources: Dict[str, Any] = None) -> bool:
        """Set up finite volume options configuration."""
        return self.fv_options.configure(
            write_fv_options=write_fv_options,
            momentum_sources=momentum_sources,
            thermal_sources=thermal_sources,
            species_sources=species_sources,
            turbulence_sources=turbulence_sources,
            pressure_sources=pressure_sources,
            volume_fraction_sources=volume_fraction_sources,
            advanced_sources=advanced_sources
        )
    
    def setup_gravity_field(self, write_gravity_field: bool, gravity_value: tuple,
                            dimensions: list = None) -> bool:
        """Set up gravity field configuration."""
        return self.gravity_field.configure(
            write_gravity_field=write_gravity_field,
            gravity_value=gravity_value,
            dimensions=dimensions
        )
    
    def setup_set_fields(self, write_set_fields_dict: bool, default_field_values: Dict[str, Any] = None,
                         regions: Dict[str, Any] = None) -> bool:
        """Set up setFields configuration."""
        return self.set_fields.configure(
            write_set_fields_dict=write_set_fields_dict,
            default_field_values=default_field_values,
            regions=regions
        )
    
    def setup_decompose_par(self, write_decompose_par_dict: bool, number_of_subdomains: int,
                            method: str, coeffs: Dict[str, Any] = None, options: Dict[str, Any] = None,
                            fields: list = None, preserve_patches: list = None, preserve_cell_zones: list = None,
                            preserve_face_zones: list = None, preserve_point_zones: list = None) -> bool:
        """Set up decomposePar configuration."""
        return self.decompose_par.configure(
            write_decompose_par_dict=write_decompose_par_dict,
            number_of_subdomains=number_of_subdomains,
            method=method,
            coeffs=coeffs,
            options=options,
            fields=fields,
            preserve_patches=preserve_patches,
            preserve_cell_zones=preserve_cell_zones,
            preserve_face_zones=preserve_face_zones,
            preserve_point_zones=preserve_point_zones
        )
    
    def setup_snappy_hex_mesh(self, write_snappy_hex_mesh_dict: bool, geometry: Dict[str, Any],
                              castellated_mesh_controls: Dict[str, Any], snap_controls: Dict[str, Any],
                              add_layers_controls: Dict[str, Any] = None, mesh_quality_controls: Dict[str, Any] = None,
                              merged_patches: list = None, write_flags: Dict[str, Any] = None) -> bool:
        """Set up snappyHexMesh configuration."""
        return self.snappy_hex_mesh.configure(
            write_snappy_hex_mesh_dict=write_snappy_hex_mesh_dict,
            geometry=geometry,
            castellated_mesh_controls=castellated_mesh_controls,
            snap_controls=snap_controls,
            add_layers_controls=add_layers_controls,
            mesh_quality_controls=mesh_quality_controls,
            merged_patches=merged_patches,
            write_flags=write_flags
        )
    
    def setup_p_field(self, write_p_field: bool, internal_pressure: float,
                      boundary_conditions: Dict[str, Any], ref_pressure_cell: int = 0,
                      ref_pressure_value: float = 0.0, pressure_dimensions: list = None) -> bool:
        """Set up pressure field configuration."""
        return self.p_field.configure(
            write_p_field=write_p_field,
            internal_pressure=internal_pressure,
            boundary_conditions=boundary_conditions,
            ref_pressure_cell=ref_pressure_cell,
            ref_pressure_value=ref_pressure_value,
            pressure_dimensions=pressure_dimensions
        )
    
    def setup_u_field(self, write_u_field: bool, internal_velocity: tuple,
                      boundary_conditions: Dict[str, Any], velocity_dimensions: list = None) -> bool:
        """Set up velocity field configuration."""
        return self.u_field.configure(
            write_u_field=write_u_field,
            internal_velocity=internal_velocity,
            boundary_conditions=boundary_conditions,
            velocity_dimensions=velocity_dimensions
        )
    
    def setup_f_field(self, write_f_field: bool, internal_force: tuple,
                      boundary_conditions: Dict[str, Any], force_dimensions: list = None) -> bool:
        """Set up force field configuration."""
        return self.f_field.configure(
            write_f_field=write_f_field,
            internal_force=internal_force,
            boundary_conditions=boundary_conditions,
            force_dimensions=force_dimensions
        )
    
    def setup_lambda_field(self, write_lambda_field: bool, internal_lambda: float,
                           boundary_conditions: Dict[str, Any], lambda_dimensions: list = None) -> bool:
        """Set up lambda field configuration."""
        return self.lambda_field.configure(
            write_lambda_field=write_lambda_field,
            internal_lambda=internal_lambda,
            boundary_conditions=boundary_conditions,
            lambda_dimensions=lambda_dimensions
        )
    
    def create_full_case(self) -> bool:
        """
        Create a complete OpenFOAM case with all configuration files.
        
        Returns:
            bool: True if all files created successfully, False otherwise.
        """
        print(f"--- Starting full OpenFOAM case setup for '{self.case_name}' ---")
        
        # Validate all components first
        if not self.validate_all_components():
            print("Component validation failed. Cannot proceed with case creation.")
            self.print_component_status()
            return False
        
        print("\nAll components validated successfully. Proceeding with case creation...")
        
        success = True
        step = 1
        total_steps = len([c for c in self.components if c.is_configured])
        
        # Build each configured component
        for component in self.components:
            if component.is_configured:
                print(f"\n[Step {step}/{total_steps}] Creating {component.name}...")
                if not component.build(self.case_name):
                    print(f"Failed to build {component.name}")
                    success = False
                step += 1
        
        if success:
            print(f"\n--- Case setup complete! ---")
            print(f"Files written in '{self.case_name}':")
            
            # List all created files
            created_files = []
            
            # System files
            if self.geometry.is_configured:
                created_files.append(os.path.join(self.case_name, 'system', 'blockMeshDict'))
            if self.control.is_configured:
                created_files.append(os.path.join(self.case_name, 'system', 'controlDict'))
            
            # Constant files
            if self.turbulence.is_configured:
                created_files.append(os.path.join(self.case_name, 'constant', 'turbulenceProperties'))
            if self.dynamic_mesh.is_configured and self.dynamic_mesh.write_dynamic_mesh_dict:
                created_files.append(os.path.join(self.case_name, 'constant', 'dynamicMeshDict'))
            if self.hfdibdem.is_configured and self.hfdibdem.write_hfdibdem_dict:
                created_files.append(os.path.join(self.case_name, 'constant', 'HFDIBDEMDict'))
            if self.transport_properties.is_configured and self.transport_properties.write_transport_properties:
                created_files.append(os.path.join(self.case_name, 'constant', 'transportProperties'))
            if self.gravity_field.is_configured and self.gravity_field.write_gravity_field:
                created_files.append(os.path.join(self.case_name, 'constant', 'g'))
            
            # Additional system files
            if self.fv_schemes.is_configured and self.fv_schemes.write_fv_schemes:
                created_files.append(os.path.join(self.case_name, 'system', 'fvSchemes'))
            if self.fv_options.is_configured and self.fv_options.write_fv_options:
                created_files.append(os.path.join(self.case_name, 'system', 'fvOptions'))
            if self.set_fields.is_configured and self.set_fields.write_set_fields_dict:
                created_files.append(os.path.join(self.case_name, 'system', 'setFieldsDict'))
            if self.decompose_par.is_configured and self.decompose_par.write_decompose_par_dict:
                created_files.append(os.path.join(self.case_name, 'system', 'decomposeParDict'))
            if self.snappy_hex_mesh.is_configured and self.snappy_hex_mesh.write_snappy_hex_mesh_dict:
                created_files.append(os.path.join(self.case_name, 'system', 'snappyHexMeshDict'))
            
            # Zero directory files
            if self.p_field.is_configured and self.p_field.write_p_field:
                created_files.append(os.path.join(self.case_name, '0', 'p'))
            if self.u_field.is_configured and self.u_field.write_u_field:
                created_files.append(os.path.join(self.case_name, '0', 'U'))
            if self.f_field.is_configured and self.f_field.write_f_field:
                created_files.append(os.path.join(self.case_name, '0', 'f'))
            if self.lambda_field.is_configured and self.lambda_field.write_lambda_field:
                created_files.append(os.path.join(self.case_name, '0', 'lambda'))
            
            for file_path in created_files:
                print(f"  - {file_path}")
                
        else:
            print(f"\n--- Case setup failed! ---")
            print("Some components could not be built. Check error messages above.")
        
        return success
