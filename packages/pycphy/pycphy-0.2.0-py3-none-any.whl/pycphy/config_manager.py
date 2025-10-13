# config_manager.py

"""
Configuration manager for pycphy package.

This module provides utilities for loading and managing configuration files
from user-specified directories or the package's default configurations.
"""

from pathlib import Path
from typing import Optional
import importlib.util


class ConfigManager:
    """
    Manager for loading and accessing configuration files.
    
    This class handles loading configuration modules from user directories
    or falling back to package defaults.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir (str, optional): Directory containing user config files.
        """
        self.config_dir = Path(config_dir) if config_dir else None
        self.configs = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all available configuration modules."""
        # List of required config modules
        config_modules = [
            'global_config',
            'block_mesh_config', 
            'control_config',
            'turbulence_config',
            'dynamic_mesh_config',
            'config_hfdibdem',
            'transport_properties_config',
            'fv_schemes_config',
            'fv_options_config',
            'gravity_field_config',
            'set_fields_config',
            'decompose_par_config',
            'snappy_hex_mesh_config'
        ]
        
        for module_name in config_modules:
            self._load_config_module(module_name)
    
    def _load_config_module(self, module_name: str):
        """
        Load a specific configuration module.
        
        Args:
            module_name (str): Name of the configuration module.
        """
        # Try to load from user config directory first
        if self.config_dir:
            config_file = self.config_dir / f"{module_name}.py"
            if config_file.exists():
                try:
                    spec = importlib.util.spec_from_file_location(module_name, config_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.configs[module_name] = module
                    return
                except Exception as e:
                    print(f"Warning: Could not load {config_file}: {e}")
        
        # Fall back to package default
        try:
            from pycphy.foamCaseDeveloper.config import (
                global_config,
                config_hfdibdem,
                # Constant directory configs
                turbulence_config,
                transport_properties_config,
                dynamic_mesh_config,
                gravity_field_config,
                # System directory configs
                block_mesh_config,
                control_config,
                fv_schemes_config,
                fv_options_config,
                set_fields_config,
                decompose_par_config,
                snappy_hex_mesh_config,
                # Zero directory configs
                p_config,
                U_config,
                f_config,
                lambda_config
            )
            
            config_map = {
                'global_config': global_config,
                'config_hfdibdem': config_hfdibdem,
                # Constant directory configs
                'turbulence_config': turbulence_config,
                'transport_properties_config': transport_properties_config,
                'dynamic_mesh_config': dynamic_mesh_config,
                'gravity_field_config': gravity_field_config,
                # System directory configs
                'block_mesh_config': block_mesh_config,
                'control_config': control_config,
                'fv_schemes_config': fv_schemes_config,
                'fv_options_config': fv_options_config,
                'set_fields_config': set_fields_config,
                'decompose_par_config': decompose_par_config,
                'snappy_hex_mesh_config': snappy_hex_mesh_config,
                # Zero directory configs
                'p_config': p_config,
                'u_config': U_config,
                'f_config': f_config,
                'lambda_config': lambda_config
            }
            
            if module_name in config_map:
                self.configs[module_name] = config_map[module_name]
                
        except ImportError as e:
            print(f"Warning: Could not load default {module_name}: {e}")
    
    def get_config(self, config_name: str):
        """
        Get a configuration module.
        
        Args:
            config_name (str): Name of the configuration module.
            
        Returns:
            Configuration module object.
        """
        if config_name not in self.configs:
            self._load_config_module(config_name)
        return self.configs.get(config_name)
    
    def get_geometry_config(self):
        """Get geometry configuration."""
        return self.get_config('block_mesh_config')
    
    def get_control_config(self):
        """Get control configuration."""
        return self.get_config('control_config')
    
    def get_turbulence_config(self):
        """Get turbulence configuration."""
        return self.get_config('turbulence_config')
    
    def get_dynamic_mesh_config(self):
        """Get dynamic mesh configuration."""
        return self.get_config('dynamic_mesh_config')
    
    def get_hfdibdem_config(self):
        """Get HFDIBDEM configuration."""
        return self.get_config('config_hfdibdem')
    
    def get_global_config(self):
        """Get global configuration."""
        return self.get_config('global_config')
    
    def validate_configs(self) -> bool:
        """
        Validate all loaded configurations.
        
        Returns:
            bool: True if all configs are valid, False otherwise.
        """
        valid = True
        
        # Check required configs
        required_configs = ['global_config', 'block_mesh_config', 'control_config', 'turbulence_config']
        for config_name in required_configs:
            if config_name not in self.configs:
                print(f"Error: Required configuration '{config_name}' not found")
                valid = False
        
        return valid
    
    def print_config_summary(self):
        """Print a summary of loaded configurations."""
        print("Configuration Summary:")
        print("=" * 50)
        
        for config_name, config in self.configs.items():
            if config_name == 'global_config':
                case_name = getattr(config, 'case_name', 'Unknown')
                print(f"Global: Case name = '{case_name}'")
            elif config_name == 'block_mesh_config':
                p0 = getattr(config, 'p0', 'Unknown')
                p1 = getattr(config, 'p1', 'Unknown')
                cells = getattr(config, 'cells', 'Unknown')
                print(f"Geometry: Domain {p0} to {p1}, Cells {cells}")
            elif config_name == 'control_config':
                app = getattr(config, 'control_params', {}).get('application', 'Unknown')
                print(f"Control: Solver = '{app}'")
            elif config_name == 'turbulence_config':
                sim_type = getattr(config, 'SIMULATION_TYPE', 'Unknown')
                print(f"Turbulence: Type = '{sim_type}'")
            elif config_name == 'dynamic_mesh_config':
                enabled = getattr(config, 'WRITE_DYNAMIC_MESH_DICT', False)
                mesh_type = getattr(config, 'MESH_TYPE', 'Unknown')
                print(f"Dynamic Mesh: Enabled = {enabled}, Type = '{mesh_type}'")
            elif config_name == 'config_hfdibdem':
                enabled = getattr(config, 'WRITE_HFDIBDEM_DICT', False)
                bodies = getattr(config, 'SELECTED_BODY_NAMES', [])
                print(f"HFDIBDEM: Enabled = {enabled}, Bodies = {bodies}")
        
        print("=" * 50)


def create_config_from_template(config_name: str, output_dir: str = ".") -> bool:
    """
    Create a configuration file from template.
    
    Args:
        config_name (str): Name of the configuration to create.
        output_dir (str): Directory to create the file.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    output_path = Path(output_dir)
    
    templates = {
        "global_config.py": """# Global configuration for OpenFOAM case
case_name = "myCase"
case_description = "My OpenFOAM simulation case"
author_name = "Your Name"
output_directory = "."
verbose_output = True
creation_date = "2025-01-09"
""",
        "block_mesh_config.py": """# Geometry configuration for blockMeshDict
p0 = (0.0, 0.0, 0.0)  # Minimum corner (x0, y0, z0)
p1 = (1.0, 0.5, 0.2)  # Maximum corner (x1, y1, z1)
cells = (50, 25, 10)   # Number of cells (nx, ny, nz)
patch_names = {
    'minX': 'inlet',
    'maxX': 'outlet',
    'minY': 'frontWall',
    'maxY': 'backWall',
    'minZ': 'floor',
    'maxZ': 'ceiling'
}
scale = 1.0
""",
        "control_config.py": """# Control configuration for controlDict
control_params = {
    'application': 'simpleFoam',
    'startFrom': 'startTime',
    'startTime': 0,
    'stopAt': 'endTime',
    'endTime': 100,
    'deltaT': 0.001,
    'writeControl': 'timeStep',
    'writeInterval': 10,
    'purgeWrite': 2,
    'writeFormat': 'ascii',
    'writePrecision': 6,
    'writeCompression': 'off',
    'timeFormat': 'general',
    'timePrecision': 6,
    'runTimeModifiable': 'true',
    'maxCo': 0.5,
    'maxDeltaT': 0.001
}
""",
        "turbulence_config.py": """# Turbulence configuration for turbulenceProperties
SIMULATION_TYPE = "RAS"  # Options: "RAS", "LES", "laminar"
turbulenceOn = True

# RAS Model Properties
RAS_PROPERTIES = {
    'RASModel': 'kEpsilon',
    'turbulence': 'on',
    'printCoeffs': 'on'
}

# LES Model Properties
LES_PROPERTIES = {
    'LESModel': 'Smagorinsky',
    'turbulence': 'on',
    'printCoeffs': 'on'
}

# Laminar Properties
LAMINAR_PROPERTIES = {}
""",
        "dynamic_mesh_config.py": """# Dynamic mesh configuration (optional)
WRITE_DYNAMIC_MESH_DICT = False  # Set to True to enable
MESH_TYPE = "solidBodyMotion"  # Options: "solidBodyMotion", "multiBodyOverset", "adaptiveRefinement", "morphingMesh"

# Example solid body motion configuration
SOLID_BODY_MOTION_PROPS = {
    "dynamicFvMesh": "dynamicMotionSolverFvMesh",
    "solver": "solidBody",
    "solidBodyCoeffs": {
        "cellZone": "rotatingZone",
        "solidBodyMotionFunction": "rotatingMotion",
        "rotatingMotionCoeffs": {
            "origin": (0, 0, 0),
            "axis": (0, 0, 1),
            "omega": 10.5
        }
    }
}
""",
        "config_hfdibdem.py": """# HFDIBDEM configuration (optional)
WRITE_HFDIBDEM_DICT = False  # Set to True to enable

# Example configuration for a falling sphere
GLOBAL_SETTINGS = {
    "interpolationSchemes": {"U": "cell"},
    "surfaceThreshold": 1e-4,
    "stepDEM": 0.01,
    "geometricD": (1, 1, 1),
    "recordSimulation": True,
    "recordFirstTimeStep": False,
    "nSolidsInDomain": 1000,
    "outputSetup": {
        "basic": False,
        "iB": False,
        "DEM": False,
        "addModel": False,
        "parallelDEM": False
    }
}

SELECTED_BODY_NAMES = ["singleFallingSphere"]

AVAILABLE_BODIES = {
    "singleFallingSphere": {
        "fullyCoupledBody": {"velocity": (0, -1.0, 0)},
        "rho": "rho [1 -3 0 0 0 0 0] 2500",
        "refineMC": 5,
        "U": {"BC": "noSlip"},
        "material": "particleMat1",
        "updateTorque": True,
        "bodyGeom": "sphere",
        "sphere": {
            "radius": 0.04,
            "startPosition": (0, 0.2, 0)
        },
        "bodyAddition": {
            "addModel": "once",
            "onceCoeffs": {}
        },
        "timesToSetStatic": -1
    }
}
"""
    }
    
    if config_name not in templates:
        print(f"Error: Unknown configuration '{config_name}'")
        return False
    
    try:
        file_path = output_path / f"{config_name}.py"
        with open(file_path, 'w') as f:
            f.write(templates[config_name])
        print(f"Created {file_path}")
        return True
    except Exception as e:
        print(f"Error creating {config_name}: {e}")
        return False
