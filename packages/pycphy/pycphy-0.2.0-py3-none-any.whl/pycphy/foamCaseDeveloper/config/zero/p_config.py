# p_config.py
"""
Configuration for pressure field (p) initialization.
Based on OpenFOAM volScalarField format for pressure boundary conditions.
"""

# =============================================================================
#           *** Configuration for pressure field (p) ***
# =============================================================================

# --- Master Control ---
# Set to True to write '0/p' field file.
WRITE_P_FIELD = True

# --- Pressure Field Configuration ---
# Internal field pressure value (Pa)
INTERNAL_PRESSURE = 0.0

# --- Boundary Conditions ---
# Boundary conditions are now read from patches.csv
# Available boundary condition types:
#   "fixedValue": Fixed pressure value
#   "zeroGradient": Zero gradient (natural outflow)
#   "fixedGradient": Fixed pressure gradient
#   "timeVaryingMappedFixedValue": Time-varying mapped value
#   "slip": Slip condition (for symmetry)
#   "noSlip": No-slip condition (for walls)

# Note: Boundary conditions are automatically loaded from patches.csv
# The CSV file should have columns: RegionName, PatchName, PatchType, p, p-value

# --- Advanced Configuration ---
# Reference pressure cell and value for pressure correction
REF_PRESSURE_CELL = 0
REF_PRESSURE_VALUE = 0.0

# Pressure dimensions [mass length^-1 time^-2]
PRESSURE_DIMENSIONS = [0, 2, -2, 0, 0, 0, 0]

# --- Template Configurations ---
# Predefined configurations for common scenarios
TEMPLATE_CONFIGS = {
    "channel_flow": {
        "internal_pressure": 0.0,
        "boundary_conditions": {
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "fixedValue", "value": 0.0},
            "walls": {"type": "zeroGradient"}
        }
    },
    "cavity_flow": {
        "internal_pressure": 0.0,
        "boundary_conditions": {
            "movingWall": {"type": "zeroGradient"},
            "fixedWalls": {"type": "zeroGradient"}
        }
    },
    "pipe_flow": {
        "internal_pressure": 0.0,
        "boundary_conditions": {
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "fixedValue", "value": 0.0},
            "wall": {"type": "zeroGradient"}
        }
    },
    "backward_facing_step": {
        "internal_pressure": 0.0,
        "boundary_conditions": {
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "fixedValue", "value": 0.0},
            "step": {"type": "zeroGradient"},
            "walls": {"type": "zeroGradient"}
        }
    }
}

# Select template (set to None to use custom configuration above)
SELECTED_TEMPLATE = None  # Options: None, "channel_flow", "cavity_flow", "pipe_flow", "backward_facing_step"

# --- Custom Field Configuration ---
# Additional field properties
FIELD_PROPERTIES = {
    "include_initial_conditions": False,  # Include initial conditions file
    "include_constraint_types": False,    # Include constraint types
    "include_environment": False,         # Include environment settings
    "use_regex_patches": False,          # Use regex for patch matching
    "version": "v2510"                   # OpenFOAM version for header
}

# --- Comments and Documentation ---
FIELD_DESCRIPTION = "Pressure field initialization for CFD simulation"
FIELD_NOTES = [
    "Pressure is typically set to 0 Pa (gauge pressure) at atmospheric conditions",
    "Use zeroGradient for natural outflow boundaries",
    "Use fixedValue for specified pressure boundaries",
    "Reference pressure cell is used for pressure correction in solvers"
]
