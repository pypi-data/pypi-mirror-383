# main.py

"""
Main entry point for the foamCaseDeveloper module.

This script provides a command-line interface for creating OpenFOAM cases
using the foamCaseDeveloper tools.
"""

import argparse
import sys
import os

from .core import FoamCaseManager
from .config import global_config, block_mesh_config, control_config, turbulence_config

def create_example_case():
    """
    Create an example OpenFOAM case with default settings from config files.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    print("Creating example OpenFOAM case from config files...")
    
    # Initialize case manager with global config
    case_manager = FoamCaseManager(global_config.case_name)
    
    # Set up geometry from config file
    case_manager.setup_geometry(
        p0=block_mesh_config.p0,
        p1=block_mesh_config.p1,
        cells=block_mesh_config.cells,
        patch_names=block_mesh_config.patch_names,
        scale=block_mesh_config.scale
    )
    
    # Set up control from config file
    case_manager.setup_control(control_config.control_params)
    
    # Set up turbulence from config file
    sim_type = turbulence_config.SIMULATION_TYPE
    if sim_type == "RAS":
        model_props = turbulence_config.RAS_PROPERTIES
    elif sim_type == "LES":
        model_props = turbulence_config.LES_PROPERTIES
    elif sim_type == "laminar":
        model_props = turbulence_config.LAMINAR_PROPERTIES
    else:
        print(f"Warning: Unknown simulation type '{sim_type}'. Using laminar.")
        sim_type = "laminar"
        model_props = {}
    
    case_manager.setup_turbulence(
        simulation_type=sim_type,
        model_properties=model_props
    )
    
    # Create the complete case
    return case_manager.create_full_case()

def create_custom_case(case_name, geometry_file=None, control_file=None, turbulence_file=None):
    """
    Create a custom OpenFOAM case from configuration files.
    
    Args:
        case_name (str): Name of the case directory.
        geometry_file (str): Path to geometry configuration file.
        control_file (str): Path to control configuration file.
        turbulence_file (str): Path to turbulence configuration file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    print(f"Creating custom OpenFOAM case '{case_name}'...")
    
    # Initialize case manager
    case_manager = FoamCaseManager(case_name)
    
    # Load geometry configuration
    if geometry_file and os.path.exists(geometry_file):
        try:
            # Import the geometry configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("geometry_config", geometry_file)
            geometry_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(geometry_module)
            
            geometry_config = BlockMeshConfig(
                p0=geometry_module.p0,
                p1=geometry_module.p1,
                cells=geometry_module.cells,
                patch_names=geometry_module.patch_names,
                scale=getattr(geometry_module, 'scale', 1.0)
            )
            
            case_manager.setup_geometry(
                p0=geometry_config.p0,
                p1=geometry_config.p1,
                cells=geometry_config.cells,
                patch_names=geometry_config.patch_names,
                scale=geometry_config.scale
            )
            
        except Exception as e:
            print(f"Error loading geometry configuration: {e}")
            return False
    else:
        print("No geometry configuration file provided, using defaults.")
        geometry_config = BlockMeshConfig()
        case_manager.setup_geometry(
            p0=geometry_config.p0,
            p1=geometry_config.p1,
            cells=geometry_config.cells,
            patch_names=geometry_config.patch_names,
            scale=geometry_config.scale
        )
    
    # Load control configuration
    if control_file and os.path.exists(control_file):
        try:
            # Import the control configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("control_config", control_file)
            control_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(control_module)
            
            case_manager.setup_control(control_module.control_params)
            
        except Exception as e:
            print(f"Error loading control configuration: {e}")
            return False
    else:
        print("No control configuration file provided, using defaults.")
        control_config = ControlConfig()
        case_manager.setup_control(control_config.get_parameters())
    
    # Load turbulence configuration
    if turbulence_file and os.path.exists(turbulence_file):
        try:
            # Import the turbulence configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("turbulence_config", turbulence_file)
            turbulence_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(turbulence_module)
            
            sim_type = turbulence_module.SIMULATION_TYPE
            if sim_type == "RAS":
                model_props = turbulence_module.RAS_PROPERTIES
            elif sim_type == "LES":
                model_props = turbulence_module.LES_PROPERTIES
            elif sim_type == "laminar":
                model_props = turbulence_module.LAMINAR_PROPERTIES
            else:
                print(f"Warning: Unknown simulation type '{sim_type}'. Using laminar.")
                sim_type = "laminar"
                model_props = {}
            
            case_manager.setup_turbulence(
                simulation_type=sim_type,
                model_properties=model_props
            )
            
        except Exception as e:
            print(f"Error loading turbulence configuration: {e}")
            return False
    else:
        print("No turbulence configuration file provided, using defaults.")
        turbulence_config = TurbulenceConfig()
        case_manager.setup_turbulence(
            simulation_type=turbulence_config.get_simulation_type(),
            model_properties=turbulence_config.get_model_properties()
        )
    
    # Create the complete case
    return case_manager.create_full_case()

def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="OpenFOAM Case Developer - Create OpenFOAM cases with Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create an example case
  pycphy-foam --example
  
  # Create a custom case from configuration files
  pycphy-foam --case myCase --geometry configBlockMesh.py --control configControl.py --turbulence configTurbulence.py
  
  # Create a case with just geometry configuration
  pycphy-foam --case myCase --geometry configBlockMesh.py
        """
    )
    
    parser.add_argument(
        "--example",
        action="store_true",
        help="Create an example OpenFOAM case with default settings"
    )
    
    parser.add_argument(
        "--case",
        type=str,
        help="Name of the OpenFOAM case directory to create"
    )
    
    parser.add_argument(
        "--geometry",
        type=str,
        help="Path to geometry configuration file (Python module)"
    )
    
    parser.add_argument(
        "--control",
        type=str,
        help="Path to control configuration file (Python module)"
    )
    
    parser.add_argument(
        "--turbulence",
        type=str,
        help="Path to turbulence configuration file (Python module)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.example and args.case:
        print("Error: Cannot specify both --example and --case options.")
        sys.exit(1)
    
    if not args.example and not args.case:
        print("Error: Must specify either --example or --case option.")
        sys.exit(1)
    
    # Create the case
    success = False
    
    if args.example:
        success = create_example_case()
    else:
        success = create_custom_case(
            case_name=args.case,
            geometry_file=args.geometry,
            control_file=args.control,
            turbulence_file=args.turbulence
        )
    
    if success:
        print("\nOpenFOAM case creation completed successfully!")
        sys.exit(0)
    else:
        print("\nOpenFOAM case creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
