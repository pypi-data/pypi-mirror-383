"""
CSV Boundary Condition Reader

This module reads boundary condition information from patches.csv and provides
it to the zero field writers in the correct format.
"""

import csv
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PatchBoundaryCondition:
    """Data structure for patch boundary conditions."""
    region_name: str
    patch_name: str
    patch_type: str
    p_type: str
    u_type: str
    f_type: str
    lambda_type: str
    p_value: Optional[str] = None
    u_value: Optional[str] = None
    f_value: Optional[str] = None
    lambda_value: Optional[str] = None


class CSVBoundaryReader:
    """
    Reads boundary condition information from patches.csv file.
    """
    
    def __init__(self, csv_file_path: str = "Inputs/patches.csv"):
        """
        Initialize the CSV boundary reader.
        
        Args:
            csv_file_path: Path to the patches.csv file
        """
        self.csv_file_path = csv_file_path
        self.patches = {}
        self._load_patches()
    
    def _load_patches(self) -> None:
        """Load patch information from CSV file."""
        try:
            with open(self.csv_file_path, mode='r', newline='') as infile:
                reader = csv.DictReader(infile)
                
                # Check for required columns
                required_columns = [
                    'RegionName', 'PatchName', 'PatchType', 
                    'p', 'U', 'f', 'lambda'
                ]
                
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = set(required_columns) - set(reader.fieldnames)
                    raise KeyError(f"CSV file missing required columns: {missing}")
                
                for row in reader:
                    patch_name = row['PatchName']
                    
                    # Parse boundary condition types
                    p_type = row['p'].strip() if row['p'] else 'zeroGradient'
                    u_type = row['U'].strip() if row['U'] else 'noSlip'
                    f_type = row['f'].strip() if row['f'] else 'zeroGradient'
                    lambda_type = row['lambda'].strip() if row['lambda'] else 'fixedValue'
                    
                    # Parse values (if provided)
                    p_value = row.get('p-value', '').strip() or None
                    u_value = row.get('U-value', '').strip() or None
                    f_value = row.get('f-value', '').strip() or None
                    lambda_value = row.get('lambda-value', '').strip() or None
                    
                    self.patches[patch_name] = PatchBoundaryCondition(
                        region_name=row['RegionName'],
                        patch_name=patch_name,
                        patch_type=row['PatchType'],
                        p_type=p_type,
                        u_type=u_type,
                        f_type=f_type,
                        lambda_type=lambda_type,
                        p_value=p_value,
                        u_value=u_value,
                        f_value=f_value,
                        lambda_value=lambda_value
                    )
            
            print(f"Loaded {len(self.patches)} patches from {self.csv_file_path}")
            
        except FileNotFoundError:
            print(f"Warning: {self.csv_file_path} not found. Using default boundary conditions.")
            self.patches = {}
        except Exception as e:
            print(f"Error loading patches from CSV: {e}")
            self.patches = {}
    
    def get_pressure_boundary_conditions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get pressure boundary conditions in the format expected by PFieldWriter.
        
        Returns:
            Dictionary of boundary conditions for pressure field
        """
        boundary_conditions = {}
        
        for patch_name, patch in self.patches.items():
            bc = {
                'type': patch.p_type
            }
            
            # Add value if specified
            if patch.p_value is not None and patch.p_value != '':
                try:
                    bc['value'] = float(patch.p_value)
                except ValueError:
                    bc['value'] = patch.p_value
            
            boundary_conditions[patch_name] = bc
        
        return boundary_conditions
    
    def get_velocity_boundary_conditions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get velocity boundary conditions in the format expected by UFieldWriter.
        
        Returns:
            Dictionary of boundary conditions for velocity field
        """
        boundary_conditions = {}
        
        for patch_name, patch in self.patches.items():
            bc = {
                'type': patch.u_type
            }
            
            # Add value if specified
            if patch.u_value is not None and patch.u_value != '':
                try:
                    # Try to parse as vector (x, y, z)
                    if ',' in patch.u_value:
                        values = [float(x.strip()) for x in patch.u_value.split(',')]
                        bc['value'] = tuple(values)
                    else:
                        bc['value'] = float(patch.u_value)
                except ValueError:
                    bc['value'] = patch.u_value
            
            boundary_conditions[patch_name] = bc
        
        return boundary_conditions
    
    def get_force_boundary_conditions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get force boundary conditions in the format expected by FFieldWriter.
        
        Returns:
            Dictionary of boundary conditions for force field
        """
        boundary_conditions = {}
        
        for patch_name, patch in self.patches.items():
            bc = {
                'type': patch.f_type
            }
            
            # Add value if specified
            if patch.f_value is not None and patch.f_value != '':
                try:
                    # Try to parse as vector (x, y, z)
                    if ',' in patch.f_value:
                        values = [float(x.strip()) for x in patch.f_value.split(',')]
                        bc['value'] = tuple(values)
                    else:
                        bc['value'] = float(patch.f_value)
                except ValueError:
                    bc['value'] = patch.f_value
            
            boundary_conditions[patch_name] = bc
        
        return boundary_conditions
    
    def get_lambda_boundary_conditions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get lambda boundary conditions in the format expected by LambdaFieldWriter.
        
        Returns:
            Dictionary of boundary conditions for lambda field
        """
        boundary_conditions = {}
        
        for patch_name, patch in self.patches.items():
            bc = {
                'type': patch.lambda_type
            }
            
            # Add value if specified
            if patch.lambda_value is not None and patch.lambda_value != '':
                try:
                    bc['value'] = float(patch.lambda_value)
                except ValueError:
                    bc['value'] = patch.lambda_value
            
            boundary_conditions[patch_name] = bc
        
        return boundary_conditions
    
    def get_patch_names(self) -> List[str]:
        """Get list of all patch names."""
        return list(self.patches.keys())
    
    def get_patch_info(self, patch_name: str) -> Optional[PatchBoundaryCondition]:
        """Get information for a specific patch."""
        return self.patches.get(patch_name)


# Global instance for easy access
csv_boundary_reader = CSVBoundaryReader()
