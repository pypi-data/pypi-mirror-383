#!/usr/bin/env python3
"""
Main script to run OpenFOAM case setup using the pycphy package with config files.

This script demonstrates how to use the pycphy.foamCaseDeveloper module
with the new configuration file structure.

Author: Sanjeev Bashyal
Location: https://github.com/SanjeevBashyal/pycphy
"""

import os
import sys
import argparse

# Add the current directory to Python path to import pycphy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pycphy.foamCaseDeveloper import FoamCaseManager, CADBlockMeshDeveloper, cad_mesh_config
from pycphy.config_manager import ConfigManager

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run pycphy OpenFOAM case builder")
    parser.add_argument("--config-dir", dest="config_dir", default=None, help="Directory containing user config .py files")
    parser.add_argument("--case-name", dest="case_name", default=None, help="Override case name from configs")
    
    # CAD-based generation options
    parser.add_argument("--cad-mode", action="store_true", default=True, help="Enable CAD-based blockMeshDict generation (default)")
    parser.add_argument("--config-mode", action="store_true", help="Use traditional config-based geometry generation instead of CAD")
    parser.add_argument("--blocks-csv", dest="blocks_csv", default="Inputs/blocks.csv", help="Path to blocks CSV file")
    parser.add_argument("--patches-csv", dest="patches_csv", default="Inputs/patches.csv", help="Path to patches CSV file")
    parser.add_argument("--cad-debug", action="store_true", help="Enable debug output for CAD processing")
    parser.add_argument("--cad-tolerance", dest="cad_tolerance", type=float, default=1e-6, help="Tolerance for CAD face matching")
    parser.add_argument("--block-xdata-app", dest="block_xdata_app", default="BLOCKDATA", help="XData app name for blocks")
    parser.add_argument("--region-xdata-app", dest="region_xdata_app", default="REGIONDATA", help="XData app name for regions")
    
    return parser.parse_args(argv)

def setup_cad_based_mesh(case_manager, args, global_config):
    """
    Set up CAD-based mesh generation using AutoCAD and CSV files.
    
    Args:
        case_manager: FoamCaseManager instance
        args: Parsed command line arguments
        global_config: Global configuration object
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\nSetting up CAD-based mesh generation...")
    
    if global_config.verbose_output:
        print(f"  - Blocks CSV: {args.blocks_csv}")
        print(f"  - Patches CSV: {args.patches_csv}")
        print(f"  - Tolerance: {args.cad_tolerance}")
        print(f"  - Block XData app: {args.block_xdata_app}")
        print(f"  - Region XData app: {args.region_xdata_app}")
        print(f"  - Debug mode: {args.cad_debug}")
    
    # Create CAD Block Mesh Developer
    cad_developer = CADBlockMeshDeveloper(
        blocks_csv_file=args.blocks_csv,
        patches_csv_file=args.patches_csv,
        tolerance=args.cad_tolerance,
        block_xdata_app_name=args.block_xdata_app,
        region_xdata_app_name=args.region_xdata_app
    )
    
    # Process CAD file and generate blockMeshDict + zero fields
    print("  Processing CAD file and generating mesh...")
    success = cad_developer.process_cad_file(
        output_path=os.path.join(case_manager.case_name, "system", "blockMeshDict"),
        debug=args.cad_debug
    )
    
    if success:
        summary = cad_developer.get_summary()
        print(f"  ✓ CAD mesh generation successful!")
        print(f"    - {summary['total_vertices']} vertices")
        print(f"    - {summary['total_blocks']} blocks")
        print(f"    - {summary['total_patches']} patches")
        print(f"    - Zero field files generated with CSV boundary conditions")
        
        # Mark geometry as ready for case creation
        case_manager.mark_geometry_ready(summary)
        case_manager.cad_mesh_summary = summary
        return True
    else:
        print(f"  ✗ CAD mesh generation failed!")
        print("    Please check:")
        print("    - AutoCAD is running with your CAD file open")
        print("    - CSV files exist and have correct format")
        print("    - XData is properly set on entities")
        return False

def main(argv=None):
    """
    Main function to demonstrate pycphy usage with config files.
    """
    args = parse_args(argv)
    
    # Handle mode selection: config-mode overrides default CAD mode
    if args.config_mode:
        use_cad_mode = False
    else:
        use_cad_mode = args.cad_mode  # Default is True
    
    print("=== pycphy: Python Computational Physics ===")
    if use_cad_mode:
        print("OpenFOAM Case Developer (CAD + Config Files)")
    else:
        print("OpenFOAM Case Developer (Config Files)")
    print("Author: Sanjeev Bashyal")
    print("=" * 50)
    cm = ConfigManager(config_dir=args.config_dir)
    if not cm.validate_configs():
        return False

    global_config = cm.get_global_config()
    block_mesh_config = cm.get_geometry_config()
    control_config = cm.get_control_config()
    turbulence_config = cm.get_turbulence_config()
    dynamic_mesh_config = cm.get_dynamic_mesh_config()
    config_hfdibdem = cm.get_hfdibdem_config()
    
    # Get new enhanced configs
    transport_properties_config = cm.get_config('transport_properties_config')
    fv_schemes_config = cm.get_config('fv_schemes_config')
    fv_options_config = cm.get_config('fv_options_config')
    gravity_field_config = cm.get_config('gravity_field_config')
    set_fields_config = cm.get_config('set_fields_config')
    decompose_par_config = cm.get_config('decompose_par_config')
    snappy_hex_mesh_config = cm.get_config('snappy_hex_mesh_config')

    # Get case name from global config
    case_name = args.case_name or getattr(global_config, 'case_name', 'pycphyCase')
    print(f"\nCreating OpenFOAM case: '{case_name}'")
    
    if global_config.verbose_output:
        print(f"Case description: {global_config.case_description}")
        print(f"Author: {global_config.author_name}")
        print(f"Output directory: {global_config.output_directory}")
    
    # Create a case manager
    case_manager = FoamCaseManager(case_name)
    
    # Set up geometry configuration
    if use_cad_mode:
        # CAD-based mesh generation
        if not setup_cad_based_mesh(case_manager, args, global_config):
            return False
    else:
        # Traditional config-based geometry setup
        print("\nSetting up geometry from config file...")
        if global_config.verbose_output:
            print(f"  - Domain: {block_mesh_config.p0} to {block_mesh_config.p1}")
            print(f"  - Cells: {block_mesh_config.cells}")
            total_cells = block_mesh_config.cells[0] * block_mesh_config.cells[1] * block_mesh_config.cells[2]
            print(f"  - Total cells: {total_cells}")
            volume = (block_mesh_config.p1[0] - block_mesh_config.p0[0]) * \
                     (block_mesh_config.p1[1] - block_mesh_config.p0[1]) * \
                     (block_mesh_config.p1[2] - block_mesh_config.p0[2])
            print(f"  - Volume: {volume:.6f}")
            print(f"  - Patch names: {block_mesh_config.patch_names}")
        
        case_manager.setup_geometry(
            p0=block_mesh_config.p0,
            p1=block_mesh_config.p1,
            cells=block_mesh_config.cells,
            patch_names=block_mesh_config.patch_names,
            scale=block_mesh_config.scale
        )
    
    # Set up control configuration from config file
    print("\nSetting up control parameters from config file...")
    if global_config.verbose_output:
        print(f"  - Solver: {control_config.control_params['application']}")
        print(f"  - Time: {control_config.control_params['startTime']} to {control_config.control_params['endTime']}")
        print(f"  - Time step: {control_config.control_params['deltaT']}")
        print(f"  - Write interval: {control_config.control_params['writeInterval']}")
        print(f"  - Write control: {control_config.control_params['writeControl']}")
        print(f"  - Courant number: {control_config.control_params['maxCo']}")
    
    case_manager.setup_control(control_config.control_params)
    
    # Set up turbulence configuration from config file
    print("\nSetting up turbulence model from config file...")
    sim_type = getattr(turbulence_config, 'SIMULATION_TYPE', 'laminar')
    if sim_type == "RAS":
        model_props = getattr(turbulence_config, 'RAS_PROPERTIES', {})
        model_name = model_props.get('RASModel', 'N/A')
    elif sim_type == "LES":
        model_props = getattr(turbulence_config, 'LES_PROPERTIES', {})
        model_name = model_props.get('LESModel', 'N/A')
    elif sim_type == "laminar":
        model_props = getattr(turbulence_config, 'LAMINAR_PROPERTIES', {})
        model_name = "laminar"
    else:
        print(f"Warning: Unknown simulation type '{sim_type}'. Using laminar.")
        sim_type = "laminar"
        model_props = {}
        model_name = "laminar"
    
    if global_config.verbose_output:
        print(f"  - Simulation type: {sim_type}")
        print(f"  - Model: {model_name}")
        print(f"  - Turbulence on: {turbulence_config.turbulenceOn}")
    
    case_manager.setup_turbulence(
        simulation_type=sim_type,
        model_properties=model_props
    )
    
    # Set up dynamic mesh configuration from config file
    print("\nSetting up dynamic mesh configuration from config file...")
    write_dynamic_mesh_dict = getattr(dynamic_mesh_config, 'WRITE_DYNAMIC_MESH_DICT', False)
    mesh_type = getattr(dynamic_mesh_config, 'MESH_TYPE', None)
    
    # Map mesh type to properties
    mesh_props_map = {
        "solidBodyMotion": getattr(dynamic_mesh_config, 'SOLID_BODY_MOTION_PROPS', {}),
        "multiBodyOverset": getattr(dynamic_mesh_config, 'MULTI_BODY_OVERSET_PROPS', {}),
        "adaptiveRefinement": getattr(dynamic_mesh_config, 'ADAPTIVE_REFINEMENT_PROPS', {}),
        "morphingMesh": getattr(dynamic_mesh_config, 'MORPHING_MESH_PROPS', {})
    }
    mesh_props = mesh_props_map.get(mesh_type)
    
    if global_config.verbose_output:
        print(f"  - Write dynamic mesh dict: {write_dynamic_mesh_dict}")
        if write_dynamic_mesh_dict:
            print(f"  - Mesh type: {mesh_type}")
            if mesh_props:
                print(f"  - Dynamic mesh properties configured")
            else:
                print(f"  - Warning: Unknown mesh type '{mesh_type}'")
    
    if write_dynamic_mesh_dict and mesh_props:
        case_manager.setup_dynamic_mesh(
            write_dynamic_mesh_dict=write_dynamic_mesh_dict,
            mesh_type=mesh_type,
            mesh_properties=mesh_props
        )
    
    # Set up HFDIBDEM configuration from config file
    print("\nSetting up HFDIBDEM configuration from config file...")
    write_hfdibdem_dict = getattr(config_hfdibdem, 'WRITE_HFDIBDEM_DICT', False)
    
    if global_config.verbose_output:
        print(f"  - Write HFDIBDEM dict: {write_hfdibdem_dict}")
        if write_hfdibdem_dict:
            selected_bodies = getattr(config_hfdibdem, 'SELECTED_BODY_NAMES', [])
            print(f"  - Selected bodies: {selected_bodies}")
            print(f"  - HFDIBDEM properties configured")
    
    if write_hfdibdem_dict:
        # Build HFDIBDEM properties dictionary
        hfdibdem_props = getattr(config_hfdibdem, 'GLOBAL_SETTINGS', {}).copy()
        
        # Add selected body names
        selected_bodies = getattr(config_hfdibdem, 'SELECTED_BODY_NAMES', [])
        hfdibdem_props["bodyNames"] = selected_bodies
        
        # Add DEM and VirtualMesh sub-dictionaries
        hfdibdem_props["DEM"] = getattr(config_hfdibdem, 'DEM_SETTINGS', {})
        hfdibdem_props["virtualMesh"] = getattr(config_hfdibdem, 'VIRTUAL_MESH_SETTINGS', {})
        
        # Add individual body configurations
        available_bodies = getattr(config_hfdibdem, 'AVAILABLE_BODIES', {})
        for name in selected_bodies:
            if name in available_bodies:
                hfdibdem_props[name] = available_bodies[name]
            else:
                print(f"  Warning: Body '{name}' not found in AVAILABLE_BODIES")
        
        case_manager.setup_hfdibdem(
            write_hfdibdem_dict=write_hfdibdem_dict,
            hfdibdem_properties=hfdibdem_props
        )
    
    # Set up transport properties configuration
    print("\nSetting up transport properties from config file...")
    write_transport_properties = getattr(transport_properties_config, 'WRITE_TRANSPORT_PROPERTIES', False)
    transport_model = getattr(transport_properties_config, 'TRANSPORT_MODEL', 'Newtonian')
    model_properties = getattr(transport_properties_config, f'{transport_model.upper()}_PROPERTIES', {})
    thermal_properties = getattr(transport_properties_config, 'THERMAL_PROPERTIES', {})
    species_properties = getattr(transport_properties_config, 'SPECIES_PROPERTIES', {})
    advanced_properties = getattr(transport_properties_config, 'ADVANCED_PROPERTIES', {})
    
    if global_config.verbose_output:
        print(f"  - Transport model: {transport_model}")
        print(f"  - Model properties: {list(model_properties.keys())}")
    
    case_manager.setup_transport_properties(
        write_transport_properties=write_transport_properties,
        transport_model=transport_model,
        model_properties=model_properties,
        thermal_properties=thermal_properties,
        species_properties=species_properties,
        advanced_properties=advanced_properties
    )
    
    # Set up finite volume schemes configuration
    print("\nSetting up finite volume schemes from config file...")
    write_fv_schemes = getattr(fv_schemes_config, 'WRITE_FV_SCHEMES_DICT', True)
    ddt_schemes = getattr(fv_schemes_config, 'DDT_SCHEMES', {})
    grad_schemes = getattr(fv_schemes_config, 'GRAD_SCHEMES', {})
    div_schemes = getattr(fv_schemes_config, 'DIV_SCHEMES', {})
    laplacian_schemes = getattr(fv_schemes_config, 'LAPLACIAN_SCHEMES', {})
    interpolation_schemes = getattr(fv_schemes_config, 'INTERPOLATION_SCHEMES', {})
    sn_grad_schemes = getattr(fv_schemes_config, 'SN_GRAD_SCHEMES', {})
    flux_required = getattr(fv_schemes_config, 'FLUX_REQUIRED', {})
    
    if global_config.verbose_output:
        print(f"  - Write fvSchemes: {write_fv_schemes}")
        print(f"  - DDT schemes: {ddt_schemes.get('default', 'N/A')}")
        print(f"  - Div schemes: {len(div_schemes)} entries")
    
    case_manager.setup_fv_schemes(
        write_fv_schemes=write_fv_schemes,
        ddt_schemes=ddt_schemes,
        grad_schemes=grad_schemes,
        div_schemes=div_schemes,
        laplacian_schemes=laplacian_schemes,
        interpolation_schemes=interpolation_schemes,
        sn_grad_schemes=sn_grad_schemes,
        flux_required=flux_required
    )
    
    # Set up finite volume options configuration
    print("\nSetting up finite volume options from config file...")
    write_fv_options = getattr(fv_options_config, 'WRITE_FV_OPTIONS_DICT', True)
    momentum_sources = getattr(fv_options_config, 'MOMENTUM_SOURCES', {})
    thermal_sources = getattr(fv_options_config, 'THERMAL_SOURCES', {})
    species_sources = getattr(fv_options_config, 'SPECIES_SOURCES', {})
    turbulence_sources = getattr(fv_options_config, 'TURBULENCE_SOURCES', {})
    pressure_sources = getattr(fv_options_config, 'PRESSURE_SOURCES', {})
    volume_fraction_sources = getattr(fv_options_config, 'VOLUME_FRACTION_SOURCES', {})
    advanced_sources = getattr(fv_options_config, 'ADVANCED_SOURCES', {})
    
    if global_config.verbose_output:
        print(f"  - Write fvOptions: {write_fv_options}")
        print(f"  - Momentum sources: {len(momentum_sources)}")
        print(f"  - Thermal sources: {len(thermal_sources)}")
    
    case_manager.setup_fv_options(
        write_fv_options=write_fv_options,
        momentum_sources=momentum_sources,
        thermal_sources=thermal_sources,
        species_sources=species_sources,
        turbulence_sources=turbulence_sources,
        pressure_sources=pressure_sources,
        volume_fraction_sources=volume_fraction_sources,
        advanced_sources=advanced_sources
    )
    
    # Set up gravity field configuration
    print("\nSetting up gravity field from config file...")
    write_gravity_field = getattr(gravity_field_config, 'WRITE_GRAVITY_FIELD_DICT', True)
    gravity_value = getattr(gravity_field_config, 'GRAVITY_VALUE', (0, 0, -9.81))
    dimensions = getattr(gravity_field_config, 'DIMENSIONS', [0, 1, -2, 0, 0, 0, 0])
    
    if global_config.verbose_output:
        print(f"  - Write gravity field: {write_gravity_field}")
        print(f"  - Gravity value: {gravity_value}")
    
    case_manager.setup_gravity_field(
        write_gravity_field=write_gravity_field,
        gravity_value=gravity_value,
        dimensions=dimensions
    )
    
    # Set up setFields configuration
    print("\nSetting up setFields from config file...")
    write_set_fields_dict = getattr(set_fields_config, 'WRITE_SET_FIELDS_DICT', True)
    default_field_values = getattr(set_fields_config, 'DEFAULT_FIELD_VALUES', {})
    regions = getattr(set_fields_config, 'REGIONS', [])
    
    if global_config.verbose_output:
        print(f"  - Write setFields: {write_set_fields_dict}")
        print(f"  - Default field values: {len(default_field_values)}")
        print(f"  - Regions: {len(regions)}")
    
    case_manager.setup_set_fields(
        write_set_fields_dict=write_set_fields_dict,
        default_field_values=default_field_values,
        regions=regions
    )
    
    # Set up decomposePar configuration
    print("\nSetting up decomposePar from config file...")
    write_decompose_par_dict = getattr(decompose_par_config, 'WRITE_DECOMPOSE_PAR_DICT', True)
    number_of_subdomains = getattr(decompose_par_config, 'NUMBER_OF_SUBDOMAINS', 4)
    method = getattr(decompose_par_config, 'METHOD', 'scotch')
    coeffs = getattr(decompose_par_config, 'COEFFS', {})
    options = getattr(decompose_par_config, 'OPTIONS', {})
    fields = getattr(decompose_par_config, 'FIELDS', [])
    preserve_patches = getattr(decompose_par_config, 'PRESERVE_PATCHES', [])
    preserve_cell_zones = getattr(decompose_par_config, 'PRESERVE_CELL_ZONES', [])
    preserve_face_zones = getattr(decompose_par_config, 'PRESERVE_FACE_ZONES', [])
    preserve_point_zones = getattr(decompose_par_config, 'PRESERVE_POINT_ZONES', [])
    
    if global_config.verbose_output:
        print(f"  - Write decomposePar: {write_decompose_par_dict}")
        print(f"  - Number of subdomains: {number_of_subdomains}")
        print(f"  - Method: {method}")
    
    case_manager.setup_decompose_par(
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
    
    # Set up snappyHexMesh configuration
    print("\nSetting up snappyHexMesh from config file...")
    write_snappy_hex_mesh_dict = getattr(snappy_hex_mesh_config, 'WRITE_SNAPPY_HEX_MESH_DICT', True)
    geometry = getattr(snappy_hex_mesh_config, 'GEOMETRY', {})
    castellated_mesh_controls = getattr(snappy_hex_mesh_config, 'CASTELLATED_MESH_CONTROLS', {})
    snap_controls = getattr(snappy_hex_mesh_config, 'SNAP_CONTROLS', {})
    add_layers_controls = getattr(snappy_hex_mesh_config, 'ADD_LAYERS_CONTROLS', {})
    mesh_quality_controls = getattr(snappy_hex_mesh_config, 'MESH_QUALITY_CONTROLS', {})
    merged_patches = getattr(snappy_hex_mesh_config, 'MERGED_PATCHES', [])
    write_flags = getattr(snappy_hex_mesh_config, 'WRITE_FLAGS', {})
    
    if global_config.verbose_output:
        print(f"  - Write snappyHexMesh: {write_snappy_hex_mesh_dict}")
        print(f"  - Geometry: {len(geometry)} entries")
        print(f"  - Max global cells: {castellated_mesh_controls.get('maxGlobalCells', 'N/A')}")
    
    case_manager.setup_snappy_hex_mesh(
        write_snappy_hex_mesh_dict=write_snappy_hex_mesh_dict,
        geometry=geometry,
        castellated_mesh_controls=castellated_mesh_controls,
        snap_controls=snap_controls,
        add_layers_controls=add_layers_controls,
        mesh_quality_controls=mesh_quality_controls,
        merged_patches=merged_patches,
        write_flags=write_flags
    )
    
    # Set up zero field configurations (skip if CAD mode - already generated)
    if not use_cad_mode:
        print("\nSetting up zero field configurations from config file...")
        
        # Load zero field configs
        p_config = cm.get_config('p_config')
        u_config = cm.get_config('u_config')
        f_config = cm.get_config('f_config')
        lambda_config = cm.get_config('lambda_config')
    else:
        print("\nSkipping zero field setup (already generated by CAD processing)")
        # Set dummy values to avoid errors
        write_p_field = False
        write_u_field = False
        write_f_field = False
        write_lambda_field = False
    
    # Set up zero fields (only if not in CAD mode)
    if not use_cad_mode:
        # Set up pressure field (p)
        write_p_field = getattr(p_config, 'WRITE_P_FIELD', False)
        internal_pressure = getattr(p_config, 'INTERNAL_PRESSURE', 0.0)
        p_boundary_conditions = getattr(p_config, 'BOUNDARY_CONDITIONS', {})
        ref_pressure_cell = getattr(p_config, 'REF_PRESSURE_CELL', 0)
        ref_pressure_value = getattr(p_config, 'REF_PRESSURE_VALUE', 0.0)
        pressure_dimensions = getattr(p_config, 'PRESSURE_DIMENSIONS', [0, 2, -2, 0, 0, 0, 0])
        
        if global_config.verbose_output:
            print(f"  - Write p field: {write_p_field}")
            print(f"  - Internal pressure: {internal_pressure}")
        
        case_manager.setup_p_field(
            write_p_field=write_p_field,
            internal_pressure=internal_pressure,
            boundary_conditions=p_boundary_conditions,
            ref_pressure_cell=ref_pressure_cell,
            ref_pressure_value=ref_pressure_value,
            pressure_dimensions=pressure_dimensions
        )
        
        # Set up velocity field (U)
        write_u_field = getattr(u_config, 'WRITE_U_FIELD', False)
        internal_velocity = getattr(u_config, 'INTERNAL_VELOCITY', (0.0, 0.0, 0.0))
        u_boundary_conditions = getattr(u_config, 'BOUNDARY_CONDITIONS', {})
        velocity_dimensions = getattr(u_config, 'VELOCITY_DIMENSIONS', [0, 1, -1, 0, 0, 0, 0])
        
        if global_config.verbose_output:
            print(f"  - Write U field: {write_u_field}")
            print(f"  - Internal velocity: {internal_velocity}")
        
        case_manager.setup_u_field(
            write_u_field=write_u_field,
            internal_velocity=internal_velocity,
            boundary_conditions=u_boundary_conditions,
            velocity_dimensions=velocity_dimensions
        )
        
        # Set up force field (f)
        write_f_field = getattr(f_config, 'WRITE_F_FIELD', False)
        internal_force = getattr(f_config, 'INTERNAL_FORCE', (0.0, 0.0, 0.0))
        f_boundary_conditions = getattr(f_config, 'BOUNDARY_CONDITIONS', {})
        force_dimensions = getattr(f_config, 'FORCE_DIMENSIONS', [0, 1, -2, 0, 0, 0, 0])
        
        if global_config.verbose_output:
            print(f"  - Write f field: {write_f_field}")
            print(f"  - Internal force: {internal_force}")
        
        case_manager.setup_f_field(
            write_f_field=write_f_field,
            internal_force=internal_force,
            boundary_conditions=f_boundary_conditions,
            force_dimensions=force_dimensions
        )
        
        # Set up lambda field (λ)
        write_lambda_field = getattr(lambda_config, 'WRITE_LAMBDA_FIELD', False)
        internal_lambda = getattr(lambda_config, 'INTERNAL_LAMBDA', 0.0)
        lambda_boundary_conditions = getattr(lambda_config, 'BOUNDARY_CONDITIONS', {})
        lambda_dimensions = getattr(lambda_config, 'LAMBDA_DIMENSIONS', [0, 0, 0, 0, 0, 0, 0])
        
        if global_config.verbose_output:
            print(f"  - Write lambda field: {write_lambda_field}")
            print(f"  - Internal lambda: {internal_lambda}")
        
        case_manager.setup_lambda_field(
            write_lambda_field=write_lambda_field,
            internal_lambda=internal_lambda,
            boundary_conditions=lambda_boundary_conditions,
            lambda_dimensions=lambda_dimensions
        )
    
    # Create the complete case
    print(f"\nCreating complete OpenFOAM case...")
    success = case_manager.create_full_case()
    
    if success:
        print(f"\n=== SUCCESS ===")
        print(f"OpenFOAM case '{case_name}' has been created successfully!")
        print(f"\nGenerated files:")
        print(f"  - {os.path.join(case_name, 'system', 'blockMeshDict')}")
        print(f"  - {os.path.join(case_name, 'system', 'controlDict')}")
        print(f"  - {os.path.join(case_name, 'constant', 'turbulenceProperties')}")
        
        # Show dynamicMeshDict if it was created
        if (write_dynamic_mesh_dict and mesh_props):
            print(f"  - {os.path.join(case_name, 'constant', 'dynamicMeshDict')}")
        
        # Show HFDIBDEMDict if it was created
        if write_hfdibdem_dict:
            print(f"  - {os.path.join(case_name, 'constant', 'HFDIBDEMDict')}")
        
        # Show transport properties if created
        if write_transport_properties:
            print(f"  - {os.path.join(case_name, 'constant', 'transportProperties')}")
        
        # Show fvSchemes if created
        if write_fv_schemes:
            print(f"  - {os.path.join(case_name, 'system', 'fvSchemes')}")
        
        # Show fvOptions if created
        if write_fv_options:
            print(f"  - {os.path.join(case_name, 'system', 'fvOptions')}")
        
        # Show gravity field if created
        if write_gravity_field:
            print(f"  - {os.path.join(case_name, 'constant', 'g')}")
        
        # Show setFields if created
        if write_set_fields_dict:
            print(f"  - {os.path.join(case_name, 'system', 'setFieldsDict')}")
        
        # Show decomposePar if created
        if write_decompose_par_dict:
            print(f"  - {os.path.join(case_name, 'system', 'decomposeParDict')}")
        
        # Show snappyHexMesh if created
        if write_snappy_hex_mesh_dict:
            print(f"  - {os.path.join(case_name, 'system', 'snappyHexMeshDict')}")
        
        # Show zero directory files if created
        if use_cad_mode:
            # Show CAD-generated zero files
            print(f"  - {os.path.join(case_name, '0', 'p')} (CAD-generated)")
            print(f"  - {os.path.join(case_name, '0', 'U')} (CAD-generated)")
            print(f"  - {os.path.join(case_name, '0', 'f')} (CAD-generated)")
            print(f"  - {os.path.join(case_name, '0', 'lambda')} (CAD-generated)")
        else:
            # Show config-generated zero files
            if write_p_field:
                print(f"  - {os.path.join(case_name, '0', 'p')}")
            if write_u_field:
                print(f"  - {os.path.join(case_name, '0', 'U')}")
            if write_f_field:
                print(f"  - {os.path.join(case_name, '0', 'f')}")
            if write_lambda_field:
                print(f"  - {os.path.join(case_name, '0', 'lambda')}")
        
        if global_config.verbose_output:
            print(f"\nCase information:")
            print(f"  - Description: {global_config.case_description}")
            print(f"  - Author: {global_config.author_name}")
            print(f"  - Created: {global_config.creation_date}")
            print(f"  - Solver: {control_config.control_params['application']}")
            print(f"  - Simulation type: {sim_type}")
            if use_cad_mode and hasattr(case_manager, 'cad_mesh_summary'):
                cad_summary = case_manager.cad_mesh_summary
                print(f"  - CAD mesh: {cad_summary['total_blocks']} blocks, {cad_summary['total_patches']} patches")
        
        print(f"\nYou can now run OpenFOAM commands like:")
        print(f"  cd {case_name}")
        if use_cad_mode:
            print(f"  # Mesh already generated from CAD")
        else:
            print(f"  blockMesh")
        print(f"  {control_config.control_params['application']}")
        return True
    else:
        print(f"\n=== FAILED ===")
        print(f"OpenFOAM case creation failed!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
