# f_config.py
"""
Configuration for force field (f) initialization.
Based on OpenFOAM volVectorField format for body force boundary conditions.
"""

# =============================================================================
#           *** Configuration for force field (f) ***
# =============================================================================

# --- Master Control ---
# Set to True to write '0/f' field file.
WRITE_F_FIELD = True

# --- Force Field Configuration ---
# Internal field force vector (N/kg or m/s²) [fx, fy, fz]
INTERNAL_FORCE = (0.0, 0.0, 0.0)

# --- Boundary Conditions ---
# Boundary conditions are now read from patches.csv
# Available boundary condition types:
#   "fixedValue": Fixed force value
#   "zeroGradient": Zero gradient (natural condition)
#   "calculated": Calculated value
#   "symmetry": Symmetry condition

# Note: Boundary conditions are automatically loaded from patches.csv
# The CSV file should have columns: RegionName, PatchName, PatchType, f, f-value

# --- Advanced Configuration ---
# Force dimensions [length time^-2] (acceleration units)
FORCE_DIMENSIONS = [0, 1, -2, 0, 0, 0, 0]

# --- Force Types ---
# Predefined force configurations for different physics
FORCE_TYPES = {
    "none": {
        "internal_force": (0.0, 0.0, 0.0),
        "description": "No body forces"
    },
    "gravity": {
        "internal_force": (0.0, 0.0, -9.81),
        "description": "Gravitational force (downward)"
    },
    "buoyancy": {
        "internal_force": (0.0, 0.0, 9.81),
        "description": "Buoyancy force (upward)"
    },
    "centrifugal": {
        "internal_force": (1.0, 0.0, 0.0),
        "description": "Centrifugal force"
    },
    "coriolis": {
        "internal_force": (0.0, 0.0, 0.0),
        "description": "Coriolis force (requires rotation)"
    },
    "electromagnetic": {
        "internal_force": (0.0, 0.0, 0.0),
        "description": "Electromagnetic body force"
    }
}

# --- Template Configurations ---
# Predefined configurations for common scenarios
TEMPLATE_CONFIGS = {
    "natural_convection": {
        "internal_force": (0.0, 0.0, -9.81),
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "forced_convection": {
        "internal_force": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "rotating_frame": {
        "internal_force": (1.0, 0.0, 0.0),
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "magnetohydrodynamics": {
        "internal_force": (0.0, 0.0, 0.0),
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "free_surface": {
        "internal_force": (0.0, 0.0, -9.81),
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "zeroGradient"},
            "outlet": {"type": "zeroGradient"},
            "atmosphere": {"type": "zeroGradient"}
        }
    }
}

# Select template (set to None to use custom configuration above)
SELECTED_TEMPLATE = None  # Options: None, "natural_convection", "forced_convection", "rotating_frame", "magnetohydrodynamics", "free_surface"

# --- Custom Field Configuration ---
# Additional field properties
FIELD_PROPERTIES = {
    "include_initial_conditions": False,  # Include initial conditions file
    "include_constraint_types": False,    # Include constraint types
    "include_environment": False,         # Include environment settings
    "use_regex_patches": False,          # Use regex for patch matching
    "version": "v2510"                   # OpenFOAM version for header
}

# --- Force Source Configuration ---
# For spatially varying or time-dependent forces
FORCE_SOURCES = {
    "enabled": False,
    "source_type": "uniform",  # uniform, linear, parabolic, custom
    "custom_function": None,   # Custom force function
    "region_based": False,     # Apply forces only to specific regions
    "regions": []              # List of regions for region-based forces
}

# --- Comments and Documentation ---
FIELD_DESCRIPTION = "Body force field initialization for CFD simulation"
FIELD_NOTES = [
    "Force field represents body forces per unit mass (acceleration units)",
    "Common applications: gravity, buoyancy, centrifugal, electromagnetic forces",
    "Zero gradient is typically used for all boundaries",
    "Force field is often used with Boussinesq approximation for natural convection",
    "Consider coordinate system when defining force directions"
]
