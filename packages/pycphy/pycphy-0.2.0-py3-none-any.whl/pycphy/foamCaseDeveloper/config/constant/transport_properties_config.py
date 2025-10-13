# transport_properties_config.py

"""
Transport Properties Configuration for OpenFOAM cases.

This module provides comprehensive configuration options for fluid transport properties
including Newtonian and non-Newtonian models, thermal properties, and species transport.
"""

# =============================================================================
#           *** User Input for transportProperties ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'constant/transportProperties'.
WRITE_TRANSPORT_PROPERTIES = True

# --- Transport Model Selection ---
# Choose the transport model for your fluid simulation:
# Options:
#   "Newtonian": Standard Newtonian fluid (constant viscosity)
#   "NonNewtonian": Non-Newtonian fluid models (shear-thinning, etc.)
#   "BirdCarreau": Bird-Carreau viscosity model
#   "CrossPowerLaw": Cross power law viscosity model
#   "HerschelBulkley": Herschel-Bulkley model for yield stress fluids
#   "PowerLaw": Power law viscosity model
#   "Casson": Casson model for yield stress fluids
#   "GeneralizedNewtonian": General non-Newtonian model
TRANSPORT_MODEL = "Newtonian"

# =============================================================================
#           *** Newtonian Transport Properties ***
# =============================================================================
# Used when TRANSPORT_MODEL = "Newtonian"

NEWTONIAN_PROPERTIES = {
    # Dynamic viscosity in [Pa s] or kinematic viscosity in [m^2/s]
    # For incompressible flows, use kinematic viscosity (nu)
    # For compressible flows, use dynamic viscosity (mu) and specify density
    "nu": "1e-05",  # Kinematic viscosity [m^2/s] for water at 20°C
    
    # Optional: Dynamic viscosity [Pa s] (for compressible flows)
    # "mu": "1e-03",  # Dynamic viscosity [Pa s]
    
    # Optional: Density [kg/m^3] (for compressible flows)
    # "rho": "1000",  # Density [kg/m^3]
}

# =============================================================================
#           *** Non-Newtonian Transport Properties ***
# =============================================================================
# Used when TRANSPORT_MODEL = "NonNewtonian"

NON_NEWTONIAN_PROPERTIES = {
    # Base properties
    "nu": "1e-05",  # Reference kinematic viscosity [m^2/s]
    
    # Non-Newtonian model selection
    "model": "BirdCarreau",  # Options: "BirdCarreau", "CrossPowerLaw", "HerschelBulkley", "PowerLaw", "Casson"
    
    # Model coefficients
    "modelCoeffs": {
        # Bird-Carreau model coefficients
        "nu0": "1e-05",     # Zero shear rate viscosity [m^2/s]
        "nuInf": "1e-07",   # Infinite shear rate viscosity [m^2/s]
        "k": "1.0",         # Consistency index [s]
        "n": "0.5",         # Power law index
        
        # Cross power law model coefficients (alternative)
        # "nu0": "1e-05",     # Zero shear rate viscosity [m^2/s]
        # "nuInf": "1e-07",   # Infinite shear rate viscosity [m^2/s]
        # "k": "1.0",         # Consistency index [s]
        # "n": "0.5",         # Power law index
        
        # Herschel-Bulkley model coefficients (alternative)
        # "tau0": "0.1",      # Yield stress [Pa]
        # "k": "1.0",         # Consistency index [Pa s^n]
        # "n": "0.5",         # Power law index
        
        # Power law model coefficients (alternative)
        # "k": "1.0",         # Consistency index [Pa s^n]
        # "n": "0.5",         # Power law index
        
        # Casson model coefficients (alternative)
        # "tau0": "0.1",      # Yield stress [Pa]
        # "mu": "1e-03",      # Plastic viscosity [Pa s]
    }
}

# =============================================================================
#           *** Thermal Transport Properties ***
# =============================================================================
# Additional thermal properties for heat transfer simulations

THERMAL_PROPERTIES = {
    # Enable thermal properties
    "enableThermal": False,
    
    # Thermal conductivity [W/(m K)]
    "k": "0.6",  # Thermal conductivity of water at 20°C
    
    # Specific heat capacity [J/(kg K)]
    "Cp": "4180",  # Specific heat of water at 20°C
    
    # Thermal diffusivity [m^2/s] (alternative to k and Cp)
    # "alpha": "1.43e-07",  # Thermal diffusivity of water at 20°C
    
    # Prandtl number (alternative to k and Cp)
    # "Pr": "7.0",  # Prandtl number of water at 20°C
}

# =============================================================================
#           *** Species Transport Properties ***
# =============================================================================
# Properties for multi-species simulations

SPECIES_PROPERTIES = {
    # Enable species transport
    "enableSpecies": False,
    
    # Number of species
    "nSpecies": 2,
    
    # Species names
    "speciesNames": ["air", "water"],
    
    # Molecular diffusivity [m^2/s] for each species
    "D": ["2e-05", "1e-09"],  # Air and water diffusivity
    
    # Schmidt number (alternative to D)
    # "Sc": ["1.0", "1000.0"],  # Schmidt numbers for air and water
}

# =============================================================================
#           *** Advanced Transport Properties ***
# =============================================================================
# Additional advanced properties for specialized simulations

ADVANCED_PROPERTIES = {
    # Enable advanced properties
    "enableAdvanced": False,
    
    # Surface tension [N/m] (for multiphase flows)
    "sigma": "0.072",  # Surface tension of water-air interface
    
    # Contact angle [degrees] (for wetting simulations)
    "contactAngle": "90",  # Neutral wetting
    
    # Compressibility [1/Pa] (for compressible flows)
    "kappa": "4.5e-10",  # Compressibility of water
    
    # Bulk viscosity [Pa s] (for compressible flows)
    "lambda": "0.0",  # Bulk viscosity (usually zero for most fluids)
    
    # Molecular weight [kg/mol] (for gas mixtures)
    "molecularWeight": "28.97",  # Molecular weight of air
    
    # Reference temperature [K]
    "TRef": "293.15",  # Reference temperature (20°C)
    
    # Reference pressure [Pa]
    "pRef": "101325",  # Reference pressure (1 atm)
}

# =============================================================================
#           *** Predefined Fluid Properties ***
# =============================================================================
# Common fluid property sets for quick configuration

PREDEFINED_FLUIDS = {
    "water_20C": {
        "nu": "1e-06",      # Kinematic viscosity [m^2/s]
        "rho": "998.2",     # Density [kg/m^3]
        "k": "0.6",         # Thermal conductivity [W/(m K)]
        "Cp": "4182",       # Specific heat [J/(kg K)]
        "sigma": "0.0728",  # Surface tension [N/m]
        "description": "Water at 20°C"
    },
    
    "air_20C": {
        "nu": "1.51e-05",   # Kinematic viscosity [m^2/s]
        "rho": "1.205",     # Density [kg/m^3]
        "k": "0.0257",      # Thermal conductivity [W/(m K)]
        "Cp": "1005",       # Specific heat [J/(kg K)]
        "sigma": "0.0",     # Surface tension [N/m]
        "description": "Air at 20°C and 1 atm"
    },
    
    "oil_sae30": {
        "nu": "1e-04",      # Kinematic viscosity [m^2/s]
        "rho": "900",       # Density [kg/m^3]
        "k": "0.15",        # Thermal conductivity [W/(m K)]
        "Cp": "2000",       # Specific heat [J/(kg K)]
        "sigma": "0.03",    # Surface tension [N/m]
        "description": "SAE 30 motor oil"
    },
    
    "blood": {
        "nu": "3e-06",      # Kinematic viscosity [m^2/s]
        "rho": "1050",      # Density [kg/m^3]
        "k": "0.5",         # Thermal conductivity [W/(m K)]
        "Cp": "3600",       # Specific heat [J/(kg K)]
        "sigma": "0.05",    # Surface tension [N/m]
        "description": "Human blood (approximate)"
    },
    
    "polymer_solution": {
        "model": "BirdCarreau",
        "nu0": "1e-04",     # Zero shear viscosity [m^2/s]
        "nuInf": "1e-06",   # Infinite shear viscosity [m^2/s]
        "k": "10.0",        # Consistency index [s]
        "n": "0.4",         # Power law index
        "description": "Typical polymer solution"
    }
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined fluid to use (overrides manual settings above)

USE_PREDEFINED_FLUID = None  # Set to fluid name from PREDEFINED_FLUIDS or None for manual config

# Example usage:
# USE_PREDEFINED_FLUID = "water_20C"  # Will use water properties at 20°C
