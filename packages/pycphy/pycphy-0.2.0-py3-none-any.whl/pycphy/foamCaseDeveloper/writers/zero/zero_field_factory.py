"""
Zero Field Factory for OpenFOAM cases.

This factory creates zero field writers using configuration files and optionally
CSV boundary conditions. It determines which fields to write based on CSV content.
"""

import os
from typing import Dict, Any, Optional, List
from ..foam_writer import FoamWriter


class ZeroFieldFactory:
    """
    Factory class to create zero field writers using config files and CSV data.
    """
    
    def __init__(self, output_dir: str = "0", csv_file_path: str = "Inputs/patches.csv"):
        """
        Initialize the zero field factory.
        
        Args:
            output_dir: Directory where to write the zero field files
            csv_file_path: Path to the patches.csv file
        """
        self.output_dir = output_dir
        self.csv_file_path = csv_file_path
        self.csv_boundary_reader = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load CSV boundary conditions if file exists
        self._load_csv_boundary_conditions()
    
    def _load_csv_boundary_conditions(self):
        """Load boundary conditions from CSV file if it exists."""
        try:
            from ...config.csv_boundary_reader import CSVBoundaryReader
            self.csv_boundary_reader = CSVBoundaryReader(self.csv_file_path)
            print(f"Loaded CSV boundary conditions from {self.csv_file_path}")
        except Exception as e:
            print(f"Could not load CSV boundary conditions: {e}")
            self.csv_boundary_reader = None
    
    def _get_csv_boundary_conditions(self, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get boundary conditions for a specific field from CSV.
        
        Args:
            field_name: Name of the field (p, U, f, lambda)
            
        Returns:
            Dictionary of boundary conditions or None if not available
        """
        if not self.csv_boundary_reader:
            return None
        
        if field_name == 'p':
            return self.csv_boundary_reader.get_pressure_boundary_conditions()
        elif field_name == 'U':
            return self.csv_boundary_reader.get_velocity_boundary_conditions()
        elif field_name == 'f':
            return self.csv_boundary_reader.get_force_boundary_conditions()
        elif field_name == 'lambda':
            return self.csv_boundary_reader.get_lambda_boundary_conditions()
        
        return None
    
    def _check_field_in_csv(self, field_name: str) -> bool:
        """
        Check if a field is defined in the CSV file.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field is defined in CSV, False otherwise
        """
        if not self.csv_boundary_reader:
            return False
        
        patches = self.csv_boundary_reader.get_patch_names()
        if not patches:
            return False
        
        # Check if any patch has non-empty values for this field
        for patch_name in patches:
            patch_info = self.csv_boundary_reader.get_patch_info(patch_name)
            if patch_info:
                if field_name == 'p' and patch_info.p_type and patch_info.p_type.strip():
                    return True
                elif field_name == 'U' and patch_info.u_type and patch_info.u_type.strip():
                    return True
                elif field_name == 'f' and patch_info.f_type and patch_info.f_type.strip():
                    return True
                elif field_name == 'lambda' and patch_info.lambda_type and patch_info.lambda_type.strip():
                    return True
        
        return False
    
    def create_pressure_writer(self, use_csv_boundaries: bool = True) -> Optional[Any]:
        """
        Create a pressure field writer using config and optionally CSV boundaries.
        
        Args:
            use_csv_boundaries: If True, use CSV boundary conditions if available
            
        Returns:
            PFieldWriter instance or None if pressure field not configured
        """
        from ...config.zero import p_config
        
        # Check if pressure field should be written
        if not p_config.WRITE_P_FIELD:
            return None
        
        # Check if field is defined in CSV (if using CSV boundaries)
        if use_csv_boundaries and not self._check_field_in_csv('p'):
            print("Pressure field not found in CSV, skipping...")
            return None
        
        # Import the writer
        from .p_field_writer import PFieldWriter
        
        # Get boundary conditions
        if use_csv_boundaries and self.csv_boundary_reader:
            boundary_conditions = self._get_csv_boundary_conditions('p')
            if boundary_conditions:
                print(f"Using CSV boundary conditions for pressure field ({len(boundary_conditions)} patches)")
            else:
                print("No CSV boundary conditions found for pressure field, using config defaults")
                boundary_conditions = {}  # Will use template or default
        else:
            boundary_conditions = {}  # Will use template or default
        
        # Use template if no boundary conditions and template is selected
        if not boundary_conditions and p_config.SELECTED_TEMPLATE:
            template = p_config.TEMPLATE_CONFIGS.get(p_config.SELECTED_TEMPLATE)
            if template:
                boundary_conditions = template.get('boundary_conditions', {})
                print(f"Using template '{p_config.SELECTED_TEMPLATE}' for pressure field")
        
        # Create writer
        file_path = os.path.join(self.output_dir, "p")
        writer = PFieldWriter(
            file_path=file_path,
            internal_pressure=p_config.INTERNAL_PRESSURE,
            boundary_conditions=boundary_conditions,
            ref_pressure_cell=p_config.REF_PRESSURE_CELL,
            ref_pressure_value=p_config.REF_PRESSURE_VALUE,
            pressure_dimensions=p_config.PRESSURE_DIMENSIONS
        )
        
        return writer
    
    def create_velocity_writer(self, use_csv_boundaries: bool = True) -> Optional[Any]:
        """
        Create a velocity field writer using config and optionally CSV boundaries.
        
        Args:
            use_csv_boundaries: If True, use CSV boundary conditions if available
            
        Returns:
            UFieldWriter instance or None if velocity field not configured
        """
        from ...config.zero import U_config
        
        # Check if velocity field should be written
        if not U_config.WRITE_U_FIELD:
            return None
        
        # Check if field is defined in CSV (if using CSV boundaries)
        if use_csv_boundaries and not self._check_field_in_csv('U'):
            print("Velocity field not found in CSV, skipping...")
            return None
        
        # Import the writer
        from .u_field_writer import UFieldWriter
        
        # Get boundary conditions
        if use_csv_boundaries and self.csv_boundary_reader:
            boundary_conditions = self._get_csv_boundary_conditions('U')
            if boundary_conditions:
                print(f"Using CSV boundary conditions for velocity field ({len(boundary_conditions)} patches)")
            else:
                print("No CSV boundary conditions found for velocity field, using config defaults")
                boundary_conditions = {}
        else:
            boundary_conditions = {}
        
        # Use template if no boundary conditions and template is selected
        if not boundary_conditions and U_config.SELECTED_TEMPLATE:
            template = U_config.TEMPLATE_CONFIGS.get(U_config.SELECTED_TEMPLATE)
            if template:
                boundary_conditions = template.get('boundary_conditions', {})
                print(f"Using template '{U_config.SELECTED_TEMPLATE}' for velocity field")
        
        # Create writer
        file_path = os.path.join(self.output_dir, "U")
        writer = UFieldWriter(
            file_path=file_path,
            internal_velocity=U_config.INTERNAL_VELOCITY,
            boundary_conditions=boundary_conditions,
            velocity_dimensions=U_config.VELOCITY_DIMENSIONS
        )
        
        return writer
    
    def create_force_writer(self, use_csv_boundaries: bool = True) -> Optional[Any]:
        """
        Create a force field writer using config and optionally CSV boundaries.
        
        Args:
            use_csv_boundaries: If True, use CSV boundary conditions if available
            
        Returns:
            FFieldWriter instance or None if force field not configured
        """
        from ...config.zero import f_config
        
        # Check if force field should be written
        if not f_config.WRITE_F_FIELD:
            return None
        
        # Check if field is defined in CSV (if using CSV boundaries)
        if use_csv_boundaries and not self._check_field_in_csv('f'):
            print("Force field not found in CSV, skipping...")
            return None
        
        # Import the writer
        from .f_field_writer import FFieldWriter
        
        # Get boundary conditions
        if use_csv_boundaries and self.csv_boundary_reader:
            boundary_conditions = self._get_csv_boundary_conditions('f')
            if boundary_conditions:
                print(f"Using CSV boundary conditions for force field ({len(boundary_conditions)} patches)")
            else:
                print("No CSV boundary conditions found for force field, using config defaults")
                boundary_conditions = {}
        else:
            boundary_conditions = {}
        
        # Use template if no boundary conditions and template is selected
        if not boundary_conditions and f_config.SELECTED_TEMPLATE:
            template = f_config.TEMPLATE_CONFIGS.get(f_config.SELECTED_TEMPLATE)
            if template:
                boundary_conditions = template.get('boundary_conditions', {})
                print(f"Using template '{f_config.SELECTED_TEMPLATE}' for force field")
        
        # Create writer
        file_path = os.path.join(self.output_dir, "f")
        writer = FFieldWriter(
            file_path=file_path,
            internal_force=f_config.INTERNAL_FORCE,
            boundary_conditions=boundary_conditions,
            force_dimensions=f_config.FORCE_DIMENSIONS
        )
        
        return writer
    
    def create_lambda_writer(self, use_csv_boundaries: bool = True) -> Optional[Any]:
        """
        Create a lambda field writer using config and optionally CSV boundaries.
        
        Args:
            use_csv_boundaries: If True, use CSV boundary conditions if available
            
        Returns:
            LambdaFieldWriter instance or None if lambda field not configured
        """
        from ...config.zero import lambda_config
        
        # Check if lambda field should be written
        if not lambda_config.WRITE_LAMBDA_FIELD:
            return None
        
        # Check if field is defined in CSV (if using CSV boundaries)
        if use_csv_boundaries and not self._check_field_in_csv('lambda'):
            print("Lambda field not found in CSV, skipping...")
            return None
        
        # Import the writer
        from .lambda_field_writer import LambdaFieldWriter
        
        # Get boundary conditions
        if use_csv_boundaries and self.csv_boundary_reader:
            boundary_conditions = self._get_csv_boundary_conditions('lambda')
            if boundary_conditions:
                print(f"Using CSV boundary conditions for lambda field ({len(boundary_conditions)} patches)")
            else:
                print("No CSV boundary conditions found for lambda field, using config defaults")
                boundary_conditions = {}
        else:
            boundary_conditions = {}
        
        # Use template if no boundary conditions and template is selected
        if not boundary_conditions and lambda_config.SELECTED_TEMPLATE:
            template = lambda_config.TEMPLATE_CONFIGS.get(lambda_config.SELECTED_TEMPLATE)
            if template:
                boundary_conditions = template.get('boundary_conditions', {})
                print(f"Using template '{lambda_config.SELECTED_TEMPLATE}' for lambda field")
        
        # Create writer
        file_path = os.path.join(self.output_dir, "lambda")
        writer = LambdaFieldWriter(
            file_path=file_path,
            internal_lambda=lambda_config.INTERNAL_LAMBDA,
            boundary_conditions=boundary_conditions,
            lambda_dimensions=lambda_config.LAMBDA_DIMENSIONS
        )
        
        return writer
    
    def write_all_fields(self, use_csv_boundaries: bool = True) -> List[str]:
        """
        Write all configured zero field files.
        
        Args:
            use_csv_boundaries: If True, use CSV boundary conditions if available
            
        Returns:
            List of field names that were written
        """
        written_fields = []
        
        print("Writing zero field files using config + CSV boundary conditions...")
        print("=" * 60)
        
        # Write pressure field
        p_writer = self.create_pressure_writer(use_csv_boundaries)
        if p_writer:
            p_writer.write()
            written_fields.append('p')
        
        # Write velocity field
        u_writer = self.create_velocity_writer(use_csv_boundaries)
        if u_writer:
            u_writer.write()
            written_fields.append('U')
        
        # Write force field
        f_writer = self.create_force_writer(use_csv_boundaries)
        if f_writer:
            f_writer.write()
            written_fields.append('f')
        
        # Write lambda field
        lambda_writer = self.create_lambda_writer(use_csv_boundaries)
        if lambda_writer:
            lambda_writer.write()
            written_fields.append('lambda')
        
        print("=" * 60)
        print(f"Written {len(written_fields)} zero field files: {', '.join(written_fields)}")
        
        return written_fields
    
    def get_available_fields(self) -> Dict[str, bool]:
        """
        Get information about which fields are available in CSV and config.
        
        Returns:
            Dictionary with field availability information
        """
        return {
            'p': {
                'csv_available': self._check_field_in_csv('p'),
                'config_enabled': False,  # Will be set by checking config
                'boundary_conditions': self._get_csv_boundary_conditions('p')
            },
            'U': {
                'csv_available': self._check_field_in_csv('U'),
                'config_enabled': False,
                'boundary_conditions': self._get_csv_boundary_conditions('U')
            },
            'f': {
                'csv_available': self._check_field_in_csv('f'),
                'config_enabled': False,
                'boundary_conditions': self._get_csv_boundary_conditions('f')
            },
            'lambda': {
                'csv_available': self._check_field_in_csv('lambda'),
                'config_enabled': False,
                'boundary_conditions': self._get_csv_boundary_conditions('lambda')
            }
        }
