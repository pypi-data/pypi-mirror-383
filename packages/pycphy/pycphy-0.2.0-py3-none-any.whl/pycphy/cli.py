"""
Command Line Interface for pycphy.

Provides commands to scaffold config files, summarize configs, and run a case.
"""

import argparse
import sys
from pathlib import Path

from .config_manager import ConfigManager, create_config_from_template
from .foamCaseDeveloper import FoamCaseManager


def cmd_init_configs(args: argparse.Namespace) -> int:
    output_dir = args.output_dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    created = True
    for name in [
        "global_config.py",
        "block_mesh_config.py",
        "control_config.py",
        "turbulence_config.py",
        "dynamic_mesh_config.py",
        "config_hfdibdem.py",
        "transport_properties_config.py",
        "fv_schemes_config.py",
        "fv_options_config.py",
        "gravity_field_config.py",
        "set_fields_config.py",
        "decompose_par_config.py",
        "snappy_hex_mesh_config.py",
    ]:
        ok = create_config_from_template(name, output_dir)
        created = created and ok
    return 0 if created else 1


def cmd_summary(args: argparse.Namespace) -> int:
    cm = ConfigManager(config_dir=args.config_dir)
    if not cm.validate_configs():
        return 1
    cm.print_config_summary()
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cm = ConfigManager(config_dir=args.config_dir)
    if not cm.validate_configs():
        return 1

    gc = cm.get_global_config()
    bmc = cm.get_geometry_config()
    cc = cm.get_control_config()
    tc = cm.get_turbulence_config()
    dmc = cm.get_dynamic_mesh_config()
    hfd = cm.get_hfdibdem_config()

    case_name = args.case_name or getattr(gc, "case_name", "pycphyCase")
    manager = FoamCaseManager(case_name)

    # Geometry
    manager.setup_geometry(
        p0=getattr(bmc, "p0"),
        p1=getattr(bmc, "p1"),
        cells=getattr(bmc, "cells"),
        patch_names=getattr(bmc, "patch_names"),
        scale=getattr(bmc, "scale", 1.0),
    )

    # Control
    manager.setup_control(getattr(cc, "control_params"))

    # Turbulence
    sim_type = getattr(tc, "SIMULATION_TYPE", "laminar")
    if sim_type == "RAS":
        model_props = getattr(tc, "RAS_PROPERTIES", {})
    elif sim_type == "LES":
        model_props = getattr(tc, "LES_PROPERTIES", {})
    else:
        model_props = getattr(tc, "LAMINAR_PROPERTIES", {})
    manager.setup_turbulence(simulation_type=sim_type, model_properties=model_props)

    # Dynamic mesh
    if getattr(dmc, "WRITE_DYNAMIC_MESH_DICT", False):
        mesh_type = getattr(dmc, "MESH_TYPE")
        props_map = {
            "solidBodyMotion": getattr(dmc, "SOLID_BODY_MOTION_PROPS", {}),
            "multiBodyOverset": getattr(dmc, "MULTI_BODY_OVERSET_PROPS", {}),
            "adaptiveRefinement": getattr(dmc, "ADAPTIVE_REFINEMENT_PROPS", {}),
            "morphingMesh": getattr(dmc, "MORPHING_MESH_PROPS", {}),
        }
        manager.setup_dynamic_mesh(
            write_dynamic_mesh_dict=True,
            mesh_type=mesh_type,
            mesh_properties=props_map.get(mesh_type, {}),
        )

    # HFDIBDEM
    if getattr(hfd, "WRITE_HFDIBDEM_DICT", False):
        props = getattr(hfd, "GLOBAL_SETTINGS", {}).copy()
        selected = getattr(hfd, "SELECTED_BODY_NAMES", [])
        props["bodyNames"] = selected
        props["DEM"] = getattr(hfd, "DEM_SETTINGS", {})
        props["virtualMesh"] = getattr(hfd, "VIRTUAL_MESH_SETTINGS", {})
        available = getattr(hfd, "AVAILABLE_BODIES", {})
        for name in selected:
            if name in available:
                props[name] = available[name]
        manager.setup_hfdibdem(True, props)

    success = manager.create_full_case()
    return 0 if success else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pycphy", description="pycphy CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-configs", help="Create editable config files in a directory")
    p_init.add_argument("output_dir", nargs="?", default="./pycphy-configs", help="Directory to write config templates")
    p_init.set_defaults(func=cmd_init_configs)

    p_sum = sub.add_parser("summary", help="Print a summary of loaded configs")
    p_sum.add_argument("--config-dir", dest="config_dir", default=None, help="Directory with user config .py files")
    p_sum.set_defaults(func=cmd_summary)

    p_run = sub.add_parser("run", help="Build a case using configs")
    p_run.add_argument("--config-dir", dest="config_dir", default=None, help="Directory with user config .py files")
    p_run.add_argument("--case-name", dest="case_name", default=None, help="Override case name from configs")
    p_run.set_defaults(func=cmd_run)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())


