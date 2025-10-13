# lambda_config.py
"""
Configuration for lambda field (λ) initialization.
Based on OpenFOAM volScalarField format for lambda boundary conditions.
Lambda is often used for level set functions, phase fields, or other scalar transport.
"""

# =============================================================================
#           *** Configuration for lambda field (λ) ***
# =============================================================================

# --- Master Control ---
# Set to True to write '0/lambda' field file.
WRITE_LAMBDA_FIELD = True

# --- Lambda Field Configuration ---
# Internal field lambda value (dimensionless)
INTERNAL_LAMBDA = 0.0

# --- Boundary Conditions ---
# Boundary conditions are now read from patches.csv
# Available boundary condition types:
#   "fixedValue": Fixed lambda value
#   "zeroGradient": Zero gradient (natural condition)
#   "calculated": Calculated value
#   "symmetry": Symmetry condition
#   "empty": Empty condition (for 2D cases)

# Note: Boundary conditions are automatically loaded from patches.csv
# The CSV file should have columns: RegionName, PatchName, PatchType, lambda, lambda-value

# --- Advanced Configuration ---
# Lambda dimensions (typically dimensionless)
LAMBDA_DIMENSIONS = [0, 0, 0, 0, 0, 0, 0]

# --- Lambda Field Types ---
# Predefined lambda configurations for different applications
LAMBDA_TYPES = {
    "level_set": {
        "internal_lambda": 0.0,
        "description": "Level set function for interface tracking",
        "range": [-1.0, 1.0]
    },
    "phase_field": {
        "internal_lambda": 0.0,
        "description": "Phase field variable",
        "range": [0.0, 1.0]
    },
    "scalar_transport": {
        "internal_lambda": 0.0,
        "description": "General scalar transport variable",
        "range": [0.0, 1.0]
    },
    "temperature_normalized": {
        "internal_lambda": 0.0,
        "description": "Normalized temperature field",
        "range": [0.0, 1.0]
    },
    "concentration": {
        "internal_lambda": 0.0,
        "description": "Species concentration field",
        "range": [0.0, 1.0]
    },
    "porosity": {
        "internal_lambda": 1.0,
        "description": "Porosity field",
        "range": [0.0, 1.0]
    }
}

# --- Template Configurations ---
# Predefined configurations for common scenarios
TEMPLATE_CONFIGS = {
    "level_set_interface": {
        "internal_lambda": 0.0,
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "fixedValue", "value": -1.0},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "phase_field_evolution": {
        "internal_lambda": 0.0,
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "fixedValue", "value": 1.0},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "scalar_transport": {
        "internal_lambda": 0.0,
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "fixedValue", "value": 1.0},
            "outlet": {"type": "zeroGradient"}
        }
    },
    "porous_medium": {
        "internal_lambda": 1.0,
        "boundary_conditions": {
            "walls": {"type": "fixedValue", "value": 0.0},
            "inlet": {"type": "fixedValue", "value": 1.0},
            "outlet": {"type": "fixedValue", "value": 1.0}
        }
    },
    "two_phase_flow": {
        "internal_lambda": 0.0,
        "boundary_conditions": {
            "walls": {"type": "zeroGradient"},
            "inlet": {"type": "fixedValue", "value": 1.0},
            "outlet": {"type": "zeroGradient"}
        }
    }
}

# Select template (set to None to use custom configuration above)
SELECTED_TEMPLATE = None  # Options: None, "level_set_interface", "phase_field_evolution", "scalar_transport", "porous_medium", "two_phase_flow"

# --- Custom Field Configuration ---
# Additional field properties
FIELD_PROPERTIES = {
    "include_initial_conditions": False,  # Include initial conditions file
    "include_constraint_types": False,    # Include constraint types
    "include_environment": False,         # Include environment settings
    "use_regex_patches": False,          # Use regex for patch matching
    "version": "v2510"                   # OpenFOAM version for header
}

# --- Lambda Field Initialization ---
# For complex initial conditions
LAMBDA_INITIALIZATION = {
    "enabled": False,
    "initialization_type": "uniform",  # uniform, linear, parabolic, custom
    "custom_function": None,           # Custom initialization function
    "region_based": False,             # Initialize based on regions
    "regions": []                      # List of regions for initialization
}

# --- Physical Properties ---
# Physical meaning and constraints
PHYSICAL_PROPERTIES = {
    "field_meaning": "General scalar field",
    "conserved_quantity": False,        # Whether lambda represents a conserved quantity
    "boundary_conditions_natural": True, # Whether zeroGradient is natural
    "initialization_critical": True,    # Whether initialization is critical
    "solver_coupling": "none"          # Coupling with other solvers
}

# --- Comments and Documentation ---
FIELD_DESCRIPTION = "Lambda field initialization for scalar transport or interface tracking"
FIELD_NOTES = [
    "Lambda is a general scalar field used for various purposes",
    "Common applications: level set functions, phase fields, scalar transport",
    "Zero gradient is typically natural for most boundaries",
    "Initial conditions are often critical for lambda field evolution",
    "Consider physical meaning when setting boundary conditions"
]
