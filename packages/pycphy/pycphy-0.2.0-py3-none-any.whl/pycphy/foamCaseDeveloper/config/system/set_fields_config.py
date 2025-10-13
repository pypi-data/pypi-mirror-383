# set_fields_config.py

"""
Set Fields Configuration for OpenFOAM cases.

This module provides configuration options for the setFields utility to initialize
field values in specific regions of the domain including cell sets, cell zones,
and geometric regions.
"""

# =============================================================================
#           *** User Input for setFieldsDict ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'system/setFieldsDict'.
WRITE_SET_FIELDS_DICT = True

# =============================================================================
#           *** Default Field Values ***
# =============================================================================
# Default values for fields that will be set in all cells unless overridden

DEFAULT_FIELD_VALUES = {
    # List of default field values
    "fields": [
        # Example: Set default volume fraction for multiphase flow
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "alpha.water",
        #     "value": 0.0,  # Default to air (0 = air, 1 = water)
        # },
        
        # Example: Set default velocity field
        # {
        #     "type": "volVectorFieldValue",
        #     "field": "U",
        #     "value": (0, 0, 0),  # Default to zero velocity
        # },
        
        # Example: Set default pressure field
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "p",
        #     "value": 0.0,  # Default to zero pressure
        # },
        
        # Example: Set default temperature field
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "T",
        #     "value": 293.15,  # Default to 20°C
        # },
        
        # Example: Set default turbulent kinetic energy
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "k",
        #     "value": 0.01,  # Default turbulent kinetic energy
        # },
        
        # Example: Set default turbulent dissipation rate
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "epsilon",
        #     "value": 0.01,  # Default turbulent dissipation rate
        # },
        
        # Example: Set default species mass fraction
        # {
        #     "type": "volScalarFieldValue",
        #     "field": "Y_CO2",
        #     "value": 0.0,  # Default CO2 mass fraction
        # },
    ]
}

# =============================================================================
#           *** Region Definitions ***
# =============================================================================
# Define regions where field values will be set

REGIONS = {
    # List of regions with specific field values
    "regions": [
        # Example: Set water in a specific region
        # {
        #     "name": "waterRegion",
        #     "type": "cellToCell",
        #     "set": "waterCells",
        #     "fieldValues": [
        #         {
        #             "type": "volScalarFieldValue",
        #             "field": "alpha.water",
        #             "value": 1.0,  # Set to water
        #         },
        #         {
        #             "type": "volVectorFieldValue",
        #             "field": "U",
        #             "value": (0, 0, 0),  # Set to zero velocity
        #         },
        #     ],
        # },
        
        # Example: Set initial velocity in inlet region
        # {
        #     "name": "inletRegion",
        #     "type": "cellToCell",
        #     "set": "inletCells",
        #     "fieldValues": [
        #         {
        #             "type": "volVectorFieldValue",
        #             "field": "U",
        #             "value": (1, 0, 0),  # Set inlet velocity
        #         },
        #     ],
        # },
        
        # Example: Set initial temperature in heated region
        # {
        #     "name": "heatedRegion",
        #     "type": "cellToCell",
        #     "set": "heatedCells",
        #     "fieldValues": [
        #         {
        #             "type": "volScalarFieldValue",
        #             "field": "T",
        #             "value": 373.15,  # Set to 100°C
        #         },
        #     ],
        # },
        
        # Example: Set initial turbulence in wake region
        # {
        #     "name": "wakeRegion",
        #     "type": "cellToCell",
        #     "set": "wakeCells",
        #     "fieldValues": [
        #         {
        #     "type": "volScalarFieldValue",
        #     "field": "k",
        #     "value": 0.1,  # Set turbulent kinetic energy
        #         },
        #         {
        #             "type": "volScalarFieldValue",
        #             "field": "epsilon",
        #             "value": 0.1,  # Set turbulent dissipation rate
        #         },
        #     ],
        # },
        
        # Example: Set initial species concentration
        # {
        #     "name": "pollutantRegion",
        #     "type": "cellToCell",
        #     "set": "pollutantCells",
        #     "fieldValues": [
        #         {
        #             "type": "volScalarFieldValue",
        #             "field": "Y_CO2",
        #             "value": 0.1,  # Set CO2 mass fraction
        #         },
        #     ],
        # },
        
        # Example: Set initial pressure
        # {
        #     "name": "highPressureRegion",
        #     "type": "cellToCell",
        #     "set": "highPressureCells",
        #     "fieldValues": [
        #         {
        #             "type": "volScalarFieldValue",
        #             "field": "p",
        #             "value": 1000.0,  # Set high pressure
        #         },
        #     ],
        # },
    ]
}

# =============================================================================
#           *** Field Value Types ***
# =============================================================================
# Available field value types for reference

FIELD_VALUE_TYPES = {
    "volScalarFieldValue": {
        "description": "Set scalar field values (pressure, temperature, etc.)",
        "example": {
            "type": "volScalarFieldValue",
            "field": "p",
            "value": 1000.0,
        }
    },
    
    "volVectorFieldValue": {
        "description": "Set vector field values (velocity, etc.)",
        "example": {
            "type": "volVectorFieldValue",
            "field": "U",
            "value": (1, 0, 0),
        }
    },
    
    "volTensorFieldValue": {
        "description": "Set tensor field values (stress, etc.)",
        "example": {
            "type": "volTensorFieldValue",
            "field": "tau",
            "value": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        }
    },
    
    "volSymmTensorFieldValue": {
        "description": "Set symmetric tensor field values",
        "example": {
            "type": "volSymmTensorFieldValue",
            "field": "R",
            "value": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        }
    },
    
    "volSphericalTensorFieldValue": {
        "description": "Set spherical tensor field values",
        "example": {
            "type": "volSphericalTensorFieldValue",
            "field": "I",
            "value": 1.0,
        }
    },
}

# =============================================================================
#           *** Region Types ***
# =============================================================================
# Available region types for reference

REGION_TYPES = {
    "cellToCell": {
        "description": "Set field values in specific cells",
        "required_fields": ["set", "fieldValues"],
        "example": {
            "name": "waterRegion",
            "type": "cellToCell",
            "set": "waterCells",
            "fieldValues": [
                {
                    "type": "volScalarFieldValue",
                    "field": "alpha.water",
                    "value": 1.0,
                },
            ],
        }
    },
    
    "cellToFace": {
        "description": "Set field values on specific faces",
        "required_fields": ["set", "fieldValues"],
        "example": {
            "name": "boundaryRegion",
            "type": "cellToFace",
            "set": "boundaryFaces",
            "fieldValues": [
                {
                    "type": "volScalarFieldValue",
                    "field": "p",
                    "value": 0.0,
                },
            ],
        }
    },
    
    "cellToPoint": {
        "description": "Set field values at specific points",
        "required_fields": ["set", "fieldValues"],
        "example": {
            "name": "pointRegion",
            "type": "cellToPoint",
            "set": "pointSet",
            "fieldValues": [
                {
                    "type": "volScalarFieldValue",
                    "field": "T",
                    "value": 373.15,
                },
            ],
        }
    },
}

# =============================================================================
#           *** Predefined Field Sets ***
# =============================================================================
# Common field initialization configurations for different simulation types

PREDEFINED_FIELD_SETS = {
    "multiphase_vof": {
        "description": "Multiphase Volume of Fluid (VOF) initialization",
        "default_fields": [
            {
                "type": "volScalarFieldValue",
                "field": "alpha.water",
                "value": 0.0,  # Default to air
            },
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
        ],
        "regions": [
            {
                "name": "waterRegion",
                "type": "cellToCell",
                "set": "waterCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "alpha.water",
                        "value": 1.0,  # Set to water
                    },
                ],
            },
        ],
    },
    
    "turbulent_flow": {
        "description": "Turbulent flow initialization",
        "default_fields": [
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
            {
                "type": "volScalarFieldValue",
                "field": "k",
                "value": 0.01,  # Default turbulent kinetic energy
            },
            {
                "type": "volScalarFieldValue",
                "field": "epsilon",
                "value": 0.01,  # Default turbulent dissipation rate
            },
        ],
        "regions": [
            {
                "name": "inletRegion",
                "type": "cellToCell",
                "set": "inletCells",
                "fieldValues": [
                    {
                        "type": "volVectorFieldValue",
                        "field": "U",
                        "value": (1, 0, 0),  # Set inlet velocity
                    },
                    {
                        "type": "volScalarFieldValue",
                        "field": "k",
                        "value": 0.1,  # Set inlet turbulence
                    },
                    {
                        "type": "volScalarFieldValue",
                        "field": "epsilon",
                        "value": 0.1,  # Set inlet dissipation
                    },
                ],
            },
        ],
    },
    
    "heat_transfer": {
        "description": "Heat transfer simulation initialization",
        "default_fields": [
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
            {
                "type": "volScalarFieldValue",
                "field": "T",
                "value": 293.15,  # Default to 20°C
            },
        ],
        "regions": [
            {
                "name": "heatedRegion",
                "type": "cellToCell",
                "set": "heatedCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "T",
                        "value": 373.15,  # Set to 100°C
                    },
                ],
            },
            {
                "name": "cooledRegion",
                "type": "cellToCell",
                "set": "cooledCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "T",
                        "value": 273.15,  # Set to 0°C
                    },
                ],
            },
        ],
    },
    
    "species_transport": {
        "description": "Species transport simulation initialization",
        "default_fields": [
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
            {
                "type": "volScalarFieldValue",
                "field": "Y_CO2",
                "value": 0.0,  # Default CO2 mass fraction
            },
            {
                "type": "volScalarFieldValue",
                "field": "Y_O2",
                "value": 0.23,  # Default O2 mass fraction (air)
            },
            {
                "type": "volScalarFieldValue",
                "field": "Y_N2",
                "value": 0.77,  # Default N2 mass fraction (air)
            },
        ],
        "regions": [
            {
                "name": "pollutantRegion",
                "type": "cellToCell",
                "set": "pollutantCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "Y_CO2",
                        "value": 0.1,  # Set CO2 mass fraction
                    },
                ],
            },
        ],
    },
    
    "compressible_flow": {
        "description": "Compressible flow simulation initialization",
        "default_fields": [
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 101325.0,  # Default to atmospheric pressure
            },
            {
                "type": "volScalarFieldValue",
                "field": "T",
                "value": 293.15,  # Default to 20°C
            },
            {
                "type": "volScalarFieldValue",
                "field": "rho",
                "value": 1.225,  # Default air density
            },
        ],
        "regions": [
            {
                "name": "highPressureRegion",
                "type": "cellToCell",
                "set": "highPressureCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "p",
                        "value": 200000.0,  # Set high pressure
                    },
                    {
                        "type": "volScalarFieldValue",
                        "field": "T",
                        "value": 373.15,  # Set high temperature
                    },
                ],
            },
        ],
    },
    
    "free_surface": {
        "description": "Free surface flow initialization",
        "default_fields": [
            {
                "type": "volScalarFieldValue",
                "field": "alpha.water",
                "value": 0.0,  # Default to air
            },
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
        ],
        "regions": [
            {
                "name": "waterRegion",
                "type": "cellToCell",
                "set": "waterCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "alpha.water",
                        "value": 1.0,  # Set to water
                    },
                ],
            },
        ],
    },
    
    "droplet_impact": {
        "description": "Droplet impact simulation initialization",
        "default_fields": [
            {
                "type": "volScalarFieldValue",
                "field": "alpha.water",
                "value": 0.0,  # Default to air
            },
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
        ],
        "regions": [
            {
                "name": "dropletRegion",
                "type": "cellToCell",
                "set": "dropletCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "alpha.water",
                        "value": 1.0,  # Set to water
                    },
                    {
                        "type": "volVectorFieldValue",
                        "field": "U",
                        "value": (0, 0, -5.0),  # Set falling velocity
                    },
                ],
            },
        ],
    },
    
    "dam_break": {
        "description": "Dam break simulation initialization",
        "default_fields": [
            {
                "type": "volScalarFieldValue",
                "field": "alpha.water",
                "value": 0.0,  # Default to air
            },
            {
                "type": "volVectorFieldValue",
                "field": "U",
                "value": (0, 0, 0),  # Default to zero velocity
            },
            {
                "type": "volScalarFieldValue",
                "field": "p",
                "value": 0.0,  # Default to zero pressure
            },
        ],
        "regions": [
            {
                "name": "waterRegion",
                "type": "cellToCell",
                "set": "waterCells",
                "fieldValues": [
                    {
                        "type": "volScalarFieldValue",
                        "field": "alpha.water",
                        "value": 1.0,  # Set to water
                    },
                ],
            },
        ],
    },
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined field set to use (overrides manual settings above)

USE_PREDEFINED_FIELD_SET = None  # Set to field set name from PREDEFINED_FIELD_SETS or None for manual config

# Example usage:
# USE_PREDEFINED_FIELD_SET = "multiphase_vof"  # Will use VOF field initialization
# USE_PREDEFINED_FIELD_SET = "turbulent_flow"  # Will use turbulent flow initialization
