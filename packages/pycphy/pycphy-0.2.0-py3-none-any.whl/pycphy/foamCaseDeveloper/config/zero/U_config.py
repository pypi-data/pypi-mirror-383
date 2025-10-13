# U_config.py
"""
Configuration for velocity field (U) initialization.
Based on OpenFOAM volVectorField format for velocity boundary conditions.
"""

# =============================================================================
#           *** Configuration for velocity field (U) ***
# =============================================================================

# --- Master Control ---
# Set to True to write '0/U' field file.
WRITE_U_FIELD = True

# --- Velocity Field Configuration ---
# Internal field velocity vector (m/s) [Ux, Uy, Uz]
INTERNAL_VELOCITY = (0.0, 0.0, 0.0)

# --- Boundary Conditions ---
# Boundary conditions are now read from patches.csv
# Available boundary condition types:
#   "fixedValue": Fixed velocity value
#   "zeroGradient": Zero gradient (natural outflow)
#   "inletOutlet": Inlet/outlet condition
#   "noSlip": No-slip condition (for walls)
#   "slip": Slip condition (for symmetry)
#   "cyclic": Cyclic boundary condition
#   "timeVaryingMappedFixedValue": Time-varying mapped value

# Note: Boundary conditions are automatically loaded from patches.csv
# The CSV file should have columns: RegionName, PatchName, PatchType, U, U-value

# --- Advanced Configuration ---
# Velocity dimensions [length time^-1]
VELOCITY_DIMENSIONS = [0, 1, -1, 0, 0, 0, 0]

# --- Flow Profile Configurations ---
# Predefined velocity profiles for different inlet conditions
FLOW_PROFILES = {
    "uniform": {
        "type": "fixedValue",
        "value": (1.0, 0.0, 0.0),
        "description": "Uniform velocity profile"
    },
    "parabolic": {
        "type": "timeVaryingMappedFixedValue",
        "description": "Parabolic velocity profile (requires profile data)"
    },
    "turbulent": {
        "type": "fixedValue", 
        "value": (1.0, 0.0, 0.0),
        "description": "Turbulent inlet (requires turbulence fields)"
    },
    "zero": {
        "type": "fixedValue",
        "value": (0.0, 0.0, 0.0),
        "description": "Zero velocity (resting fluid)"
    }
}

# --- Template Configurations ---
# Predefined configurations for common scenarios
TEMPLATE_CONFIGS = {
    "channel_flow": {
        "internal_velocity": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "inlet": {"type": "fixedValue", "value": (1.0, 0.0, 0.0)},
            "outlet": {"type": "inletOutlet", "inletValue": (0.0, 0.0, 0.0)},
            "walls": {"type": "noSlip"}
        }
    },
    "cavity_flow": {
        "internal_velocity": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "movingWall": {"type": "fixedValue", "value": (1.0, 0.0, 0.0)},
            "fixedWalls": {"type": "noSlip"}
        }
    },
    "pipe_flow": {
        "internal_velocity": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "inlet": {"type": "fixedValue", "value": (1.0, 0.0, 0.0)},
            "outlet": {"type": "inletOutlet", "inletValue": (0.0, 0.0, 0.0)},
            "wall": {"type": "noSlip"}
        }
    },
    "backward_facing_step": {
        "internal_velocity": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "inlet": {"type": "fixedValue", "value": (1.0, 0.0, 0.0)},
            "outlet": {"type": "inletOutlet", "inletValue": (0.0, 0.0, 0.0)},
            "step": {"type": "noSlip"},
            "walls": {"type": "noSlip"}
        }
    },
    "lid_driven_cavity": {
        "internal_velocity": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "movingWall": {"type": "fixedValue", "value": (1.0, 0.0, 0.0)},
            "fixedWalls": {"type": "noSlip"}
        }
    }
}

# Select template (set to None to use custom configuration above)
SELECTED_TEMPLATE = None  # Options: None, "channel_flow", "cavity_flow", "pipe_flow", "backward_facing_step", "lid_driven_cavity"

# --- Custom Field Configuration ---
# Additional field properties
FIELD_PROPERTIES = {
    "include_initial_conditions": False,  # Include initial conditions file
    "include_constraint_types": False,    # Include constraint types
    "include_environment": False,         # Include environment settings
    "use_regex_patches": False,          # Use regex for patch matching
    "version": "v2510"                   # OpenFOAM version for header
}

# --- Turbulence Inlet Configuration ---
# For cases with turbulence modeling
TURBULENCE_INLET = {
    "enabled": False,
    "turbulence_intensity": 0.05,  # 5% turbulence intensity
    "length_scale": 0.01,          # Turbulence length scale
    "profile_type": "uniform"      # uniform, parabolic, turbulent
}

# --- Comments and Documentation ---
FIELD_DESCRIPTION = "Velocity field initialization for CFD simulation"
FIELD_NOTES = [
    "Velocity is typically initialized to zero for most cases",
    "Use fixedValue for specified velocity inlets",
    "Use inletOutlet for natural outflow boundaries",
    "Use noSlip for wall boundaries",
    "Consider turbulence inlet conditions for RANS/LES simulations"
]
