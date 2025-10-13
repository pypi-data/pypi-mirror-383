# fv_options_config.py

"""
Finite Volume Options Configuration for OpenFOAM cases.

This module provides comprehensive configuration options for finite volume source terms,
constraints, and modifications including momentum sources, thermal sources, species sources,
and various constraint types.
"""

# =============================================================================
#           *** User Input for fvOptions ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'system/fvOptions'.
WRITE_FV_OPTIONS = True

# =============================================================================
#           *** Momentum Sources ***
# =============================================================================
# Source terms for momentum equations

MOMENTUM_SOURCES = {
    # Enable momentum sources
    "enabled": False,
    
    # List of momentum sources
    "sources": [
        # Example: Fixed value constraint for velocity
        # {
        #     "name": "inletVelocity",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["inlet"],
        #     "fields": ["U"],
        #     "value": "(1 0 0)",  # Fixed velocity [m/s]
        # },
        
        # Example: Momentum source term
        # {
        #     "name": "momentumSource",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "sourceRegion",
        #     "fields": ["U"],
        #     "mode": "uniform",
        #     "uniformValue": "(0 0 -9.81)",  # Gravity-like source [m/s^2]
        # },
        
        # Example: Porous media source (Darcy-Forchheimer)
        # {
        #     "name": "porousRegion",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellZone",
        #     "cellZone": "porousZone",
        #     "fields": ["U"],
        #     "mode": "uniform",
        #     "uniformValue": "(-1000*U - 100*mag(U)*U)",  # Porous resistance
        # },
        
        # Example: Actuator disk source
        # {
        #     "name": "actuatorDisk",
        #     "type": "actuatorDiskSource",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "diskRegion",
        #     "fields": ["U"],
        #     "diskDir": "(1 0 0)",
        #     "Cp": 0.4,
        #     "Ct": 0.8,
        #     "eps": 0.1,
        #     "f": 50.0,
        # },
    ]
}

# =============================================================================
#           *** Thermal Sources ***
# =============================================================================
# Source terms for energy/temperature equations

THERMAL_SOURCES = {
    # Enable thermal sources
    "enabled": False,
    
    # List of thermal sources
    "sources": [
        # Example: Fixed temperature boundary condition
        # {
        #     "name": "wallTemperature",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["hotWall"],
        #     "fields": ["T"],
        #     "value": "uniform 373.15",  # Fixed temperature [K]
        # },
        
        # Example: Heat source in region
        # {
        #     "name": "heatSource",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "heaterRegion",
        #     "fields": ["T"],
        #     "mode": "uniform",
        #     "uniformValue": "1000",  # Heat source [W/m^3]
        # },
        
        # Example: Solar radiation source
        # {
        #     "name": "solarRadiation",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "solarPanel",
        #     "fields": ["T"],
        #     "mode": "uniform",
        #     "uniformValue": "500",  # Solar heating [W/m^3]
        # },
    ]
}

# =============================================================================
#           *** Species Sources ***
# =============================================================================
# Source terms for species transport equations

SPECIES_SOURCES = {
    # Enable species sources
    "enabled": False,
    
    # List of species sources
    "sources": [
        # Example: Fixed concentration boundary
        # {
        #     "name": "inletConcentration",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["inlet"],
        #     "fields": ["Y_CO2"],
        #     "value": "uniform 0.1",  # Fixed mass fraction
        # },
        
        # Example: Species source in region
        # {
        #     "name": "pollutantSource",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "factoryRegion",
        #     "fields": ["Y_POLLUTANT"],
        #     "mode": "uniform",
        #     "uniformValue": "0.05",  # Source strength [1/s]
        # },
    ]
}

# =============================================================================
#           *** Turbulence Sources ***
# =============================================================================
# Source terms for turbulence equations

TURBULENCE_SOURCES = {
    # Enable turbulence sources
    "enabled": False,
    
    # List of turbulence sources
    "sources": [
        # Example: Fixed turbulent kinetic energy
        # {
        #     "name": "inletTurbulence",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["inlet"],
        #     "fields": ["k", "epsilon"],
        #     "value": "uniform 0.01",  # Fixed k [m^2/s^2]
        # },
        
        # Example: Turbulence source in wake region
        # {
        #     "name": "wakeTurbulence",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "wakeRegion",
        #     "fields": ["k"],
        #     "mode": "uniform",
        #     "uniformValue": "0.1",  # Turbulence generation [m^2/s^3]
        # },
    ]
}

# =============================================================================
#           *** Pressure Sources ***
# =============================================================================
# Source terms for pressure equations

PRESSURE_SOURCES = {
    # Enable pressure sources
    "enabled": False,
    
    # List of pressure sources
    "sources": [
        # Example: Fixed pressure boundary
        # {
        #     "name": "outletPressure",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["outlet"],
        #     "fields": ["p"],
        #     "value": "uniform 0",  # Fixed pressure [Pa]
        # },
        
        # Example: Pressure source in region
        # {
        #     "name": "pressureSource",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "pumpRegion",
        #     "fields": ["p"],
        #     "mode": "uniform",
        #     "uniformValue": "1000",  # Pressure source [Pa/s]
        # },
    ]
}

# =============================================================================
#           *** Volume Fraction Sources ***
# =============================================================================
# Source terms for multiphase volume fraction equations

VOLUME_FRACTION_SOURCES = {
    # Enable volume fraction sources
    "enabled": False,
    
    # List of volume fraction sources
    "sources": [
        # Example: Fixed volume fraction boundary
        # {
        #     "name": "inletAlpha",
        #     "type": "fixedValueConstraint",
        #     "active": True,
        #     "selectionMode": "all",
        #     "patchNames": ["inlet"],
        #     "fields": ["alpha.water"],
        #     "value": "uniform 1",  # Fixed volume fraction
        # },
        
        # Example: Volume fraction source (phase change)
        # {
        #     "name": "phaseChange",
        #     "type": "explicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "evaporationRegion",
        #     "fields": ["alpha.water"],
        #     "mode": "uniform",
        #     "uniformValue": "-0.1",  # Evaporation rate [1/s]
        # },
    ]
}

# =============================================================================
#           *** Advanced Sources ***
# =============================================================================
# Advanced source terms and constraints

ADVANCED_SOURCES = {
    # Enable advanced sources
    "enabled": False,
    
    # List of advanced sources
    "sources": [
        # Example: Time-varying source
        # {
        #     "name": "timeVaryingSource",
        #     "type": "timeVaryingExplicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "sourceRegion",
        #     "fields": ["U"],
        #     "timeStart": 0,
        #     "duration": 10,
        #     "value": "(sin(time*2*pi/10) 0 0)",  # Oscillating source
        # },
        
        # Example: Tabulated source
        # {
        #     "name": "tabulatedSource",
        #     "type": "tabulatedExplicitSetValue",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "sourceRegion",
        #     "fields": ["T"],
        #     "tableFile": "temperatureTable",
        #     "tableFormat": "foam",
        # },
        
        # Example: Function object source
        # {
        #     "name": "functionObjectSource",
        #     "type": "functionObjectConstraint",
        #     "active": True,
        #     "selectionMode": "cellSet",
        #     "cellSet": "monitoredRegion",
        #     "fields": ["U"],
        #     "functionObject": "fieldAverage",
        #     "functionObjectCoeffs": {
        #         "fields": ["U"],
        #         "average": True,
        #     },
        # },
    ]
}

# =============================================================================
#           *** Constraint Types ***
# =============================================================================
# Available constraint types for reference

CONSTRAINT_TYPES = {
    "fixedValueConstraint": {
        "description": "Fixed value constraint for boundary conditions",
        "required_fields": ["patchNames", "fields", "value"],
        "example": {
            "name": "inletVelocity",
            "type": "fixedValueConstraint",
            "patchNames": ["inlet"],
            "fields": ["U"],
            "value": "(1 0 0)",
        }
    },
    
    "explicitSetValue": {
        "description": "Explicit source term in field equations",
        "required_fields": ["selectionMode", "fields", "mode", "uniformValue"],
        "selection_modes": ["cellSet", "cellZone", "all", "cellSetAndSet"],
        "example": {
            "name": "momentumSource",
            "type": "explicitSetValue",
            "selectionMode": "cellSet",
            "cellSet": "sourceRegion",
            "fields": ["U"],
            "mode": "uniform",
            "uniformValue": "(0 0 -9.81)",
        }
    },
    
    "actuatorDiskSource": {
        "description": "Actuator disk model for wind turbines/propellers",
        "required_fields": ["selectionMode", "fields", "diskDir", "Cp", "Ct"],
        "example": {
            "name": "windTurbine",
            "type": "actuatorDiskSource",
            "selectionMode": "cellSet",
            "cellSet": "diskRegion",
            "fields": ["U"],
            "diskDir": "(1 0 0)",
            "Cp": 0.4,
            "Ct": 0.8,
            "eps": 0.1,
            "f": 50.0,
        }
    },
    
    "porousZone": {
        "description": "Porous media resistance model",
        "required_fields": ["selectionMode", "fields", "d", "f"],
        "example": {
            "name": "porousRegion",
            "type": "explicitSetValue",
            "selectionMode": "cellZone",
            "cellZone": "porousZone",
            "fields": ["U"],
            "mode": "uniform",
            "uniformValue": "(-1000*U - 100*mag(U)*U)",
        }
    },
    
    "timeVaryingExplicitSetValue": {
        "description": "Time-varying source term",
        "required_fields": ["selectionMode", "fields", "timeStart", "duration", "value"],
        "example": {
            "name": "pulsatingSource",
            "type": "timeVaryingExplicitSetValue",
            "selectionMode": "cellSet",
            "cellSet": "sourceRegion",
            "fields": ["U"],
            "timeStart": 0,
            "duration": 10,
            "value": "(sin(time*2*pi/10) 0 0)",
        }
    },
    
    "tabulatedExplicitSetValue": {
        "description": "Tabulated source term from file",
        "required_fields": ["selectionMode", "fields", "tableFile", "tableFormat"],
        "example": {
            "name": "tabulatedSource",
            "type": "tabulatedExplicitSetValue",
            "selectionMode": "cellSet",
            "cellSet": "sourceRegion",
            "fields": ["T"],
            "tableFile": "temperatureTable",
            "tableFormat": "foam",
        }
    },
}

# =============================================================================
#           *** Predefined Source Sets ***
# =============================================================================
# Common source configurations for different simulation types

PREDEFINED_SOURCE_SETS = {
    "channel_flow": {
        "description": "Channel flow with inlet velocity and outlet pressure",
        "momentum_sources": [
            {
                "name": "inletVelocity",
                "type": "fixedValueConstraint",
                "active": True,
                "selectionMode": "all",
                "patchNames": ["inlet"],
                "fields": ["U"],
                "value": "(1 0 0)",
            },
            {
                "name": "outletPressure",
                "type": "fixedValueConstraint",
                "active": True,
                "selectionMode": "all",
                "patchNames": ["outlet"],
                "fields": ["p"],
                "value": "uniform 0",
            },
        ],
        "thermal_sources": [],
        "species_sources": [],
        "turbulence_sources": [],
        "pressure_sources": [],
        "volume_fraction_sources": [],
        "advanced_sources": [],
    },
    
    "porous_flow": {
        "description": "Flow through porous media",
        "momentum_sources": [
            {
                "name": "porousResistance",
                "type": "explicitSetValue",
                "active": True,
                "selectionMode": "cellZone",
                "cellZone": "porousZone",
                "fields": ["U"],
                "mode": "uniform",
                "uniformValue": "(-1000*U - 100*mag(U)*U)",
            },
        ],
        "thermal_sources": [],
        "species_sources": [],
        "turbulence_sources": [],
        "pressure_sources": [],
        "volume_fraction_sources": [],
        "advanced_sources": [],
    },
    
    "wind_turbine": {
        "description": "Wind turbine simulation with actuator disk",
        "momentum_sources": [
            {
                "name": "windTurbine",
                "type": "actuatorDiskSource",
                "active": True,
                "selectionMode": "cellSet",
                "cellSet": "diskRegion",
                "fields": ["U"],
                "diskDir": "(1 0 0)",
                "Cp": 0.4,
                "Ct": 0.8,
                "eps": 0.1,
                "f": 50.0,
            },
        ],
        "thermal_sources": [],
        "species_sources": [],
        "turbulence_sources": [],
        "pressure_sources": [],
        "volume_fraction_sources": [],
        "advanced_sources": [],
    },
    
    "heat_transfer": {
        "description": "Heat transfer simulation with thermal sources",
        "momentum_sources": [],
        "thermal_sources": [
            {
                "name": "wallTemperature",
                "type": "fixedValueConstraint",
                "active": True,
                "selectionMode": "all",
                "patchNames": ["hotWall"],
                "fields": ["T"],
                "value": "uniform 373.15",
            },
            {
                "name": "heatSource",
                "type": "explicitSetValue",
                "active": True,
                "selectionMode": "cellSet",
                "cellSet": "heaterRegion",
                "fields": ["T"],
                "mode": "uniform",
                "uniformValue": "1000",
            },
        ],
        "species_sources": [],
        "turbulence_sources": [],
        "pressure_sources": [],
        "volume_fraction_sources": [],
        "advanced_sources": [],
    },
    
    "multiphase_flow": {
        "description": "Multiphase flow with volume fraction sources",
        "momentum_sources": [],
        "thermal_sources": [],
        "species_sources": [],
        "turbulence_sources": [],
        "pressure_sources": [],
        "volume_fraction_sources": [
            {
                "name": "inletAlpha",
                "type": "fixedValueConstraint",
                "active": True,
                "selectionMode": "all",
                "patchNames": ["inlet"],
                "fields": ["alpha.water"],
                "value": "uniform 1",
            },
            {
                "name": "phaseChange",
                "type": "explicitSetValue",
                "active": True,
                "selectionMode": "cellSet",
                "cellSet": "evaporationRegion",
                "fields": ["alpha.water"],
                "mode": "uniform",
                "uniformValue": "-0.1",
            },
        ],
        "advanced_sources": [],
    },
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined source set to use (overrides manual settings above)

USE_PREDEFINED_SOURCES = None  # Set to source set name from PREDEFINED_SOURCE_SETS or None for manual config

# Example usage:
# USE_PREDEFINED_SOURCES = "channel_flow"  # Will use channel flow sources
