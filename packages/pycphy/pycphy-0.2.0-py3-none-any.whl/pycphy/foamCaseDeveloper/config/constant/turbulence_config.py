# turbulence_config.py

# =============================================================================
#           *** User Input for turbulenceProperties ***
# =============================================================================
#
#   This file defines the turbulence model settings.
#   1. Set the SIMULATION_TYPE variable to 'RAS', 'LES', or 'laminar'.
#   2. Edit the corresponding properties dictionary below if needed.
#

# `SIMULATION_TYPE`: The type of turbulence simulation to perform.
# This determines which turbulence model will be used.
# Options:
#   'RAS': Reynolds-Averaged Simulation (steady or unsteady, computationally efficient)
#   'LES': Large Eddy Simulation (unsteady, more detailed but computationally expensive)
#   'laminar': Laminar flow (no turbulence model, for low Reynolds number flows)
SIMULATION_TYPE = "RAS"

# --- Reynolds-Averaged Simulation (RAS) Properties ---
# RAS models solve the Reynolds-averaged Navier-Stokes equations and model
# the effects of turbulence using statistical models. They are computationally
# less expensive and are suitable for many steady-state industrial flows.

RAS_PROPERTIES = {
    # `RASModel`: Specifies the turbulence model to use.
    # This determines how the Reynolds stresses are modeled.
    # Available Options:
    #   'kEpsilon': Standard k-epsilon model. Robust but less accurate for separated flows.
    #                Good for free shear flows, mixing layers, and jets.
    #   'realizableKE': A variation of k-epsilon with better performance for rotating flows.
    #                   Improved handling of adverse pressure gradients.
    #   'kOmega': Standard k-omega model. Good for boundary layers and adverse pressure gradients.
    #   'kOmegaSST': Menter's Shear Stress Transport model. Very popular, blends k-w
    #                near walls and k-e in the far-field. Excellent for aerodynamics
    #                and complex flows with separation.
    #   'SpalartAllmaras': One-equation model. Good for aerospace applications.
    #                      Particularly effective for attached flows.
    #   'SpalartAllmarasDDES': Detached Eddy Simulation variant of Spalart-Allmaras.
    #                          Hybrid RANS/LES model for unsteady flows.
    #   'SpalartAllmarasIDDES': Improved Delayed Detached Eddy Simulation.
    #                           Enhanced hybrid RANS/LES model.
    #   'kOmegaSSTLM': k-omega SST with Langtry-Menter transition model.
    #                  Includes laminar-turbulent transition effects.
    #   'kOmegaSSTCC': k-omega SST with curvature correction.
    #                  Better performance for flows with streamline curvature.
    #   'kOmegaSSTSAS': k-omega SST with Scale Adaptive Simulation.
    #                   Hybrid RANS/LES model for unsteady flows.
    #   'RNGkEpsilon': Renormalization Group k-epsilon model.
    #                  Improved version of standard k-epsilon.
    #   'LienLeschzinerLowRe': Low Reynolds number k-epsilon model.
    #                          Better near-wall behavior.
    #   'LaunderSharmaKE': Launder-Sharma k-epsilon model.
    #                      Low Reynolds number variant.
    #   'LamBremhorstKE': Lam-Bremhorst k-epsilon model.
    #                     Low Reynolds number variant.
    #   'ChienKE': Chien k-epsilon model.
    #              Low Reynolds number variant.
    "RASModel": "kOmegaSST",

    # `turbulence`: A switch to turn the turbulence calculations on or off.
    # This allows you to run laminar simulations with RAS setup.
    # Options: 'on' (turbulence active), 'off' (laminar simulation)
    "turbulence": "on",

    # `printCoeffs`: Prints the model coefficients to the log file at the start.
    # This is useful for debugging and verifying model settings.
    # Options: 'on' (print coefficients), 'off' (don't print)
    "printCoeffs": "on",

    # Additional RAS model coefficients (advanced users only)
    # These can be used to modify the default model coefficients if needed.
    # Most users should not modify these unless they understand the model physics.
    
    # `kEpsilonCoeffs`: Coefficients for k-epsilon models (if using kEpsilon or realizableKE)
    # "kEpsilonCoeffs": {
    #     "Cmu": 0.09,          # Turbulent viscosity coefficient
    #     "C1": 1.44,           # Production coefficient
    #     "C2": 1.92,           # Destruction coefficient
    #     "C3": -0.33,          # Buoyancy coefficient
    #     "sigmap": 1.0,        # Prandtl number for pressure
    #     "sigmak": 1.0,        # Prandtl number for k
    #     "sigmaEps": 1.3       # Prandtl number for epsilon
    # },

    # `kOmegaSSTCoeffs`: Coefficients for k-omega SST model (if using kOmegaSST)
    # "kOmegaSSTCoeffs": {
    #     "beta1": 0.075,       # Beta coefficient for k equation
    #     "beta2": 0.0828,      # Beta coefficient for omega equation
    #     "betaStar": 0.09,     # Beta star coefficient
    #     "gamma1": 0.5532,     # Gamma coefficient for k equation
    #     "gamma2": 0.4403,     # Gamma coefficient for omega equation
    #     "alphaK1": 0.85,      # Alpha coefficient for k equation
    #     "alphaK2": 1.0,       # Alpha coefficient for k equation
    #     "alphaOmega1": 0.5,   # Alpha coefficient for omega equation
    #     "alphaOmega2": 0.856, # Alpha coefficient for omega equation
    #     "Prt": 0.9            # Turbulent Prandtl number
    # },

    # `SpalartAllmarasCoeffs`: Coefficients for Spalart-Allmaras model
    # "SpalartAllmarasCoeffs": {
    #     "Cb1": 0.1355,        # Production coefficient
    #     "Cb2": 0.622,         # Destruction coefficient
    #     "sigmaNut": 0.66667,  # Turbulent viscosity coefficient
    #     "Cw1": 3.239,         # Wall destruction coefficient
    #     "Cw2": 0.3,           # Wall destruction coefficient
    #     "Cw3": 2.0,           # Wall destruction coefficient
    #     "Cv1": 7.1,           # Viscous destruction coefficient
    #     "Ct1": 1.0,           # Transition coefficient
    #     "Ct2": 2.0,           # Transition coefficient
    #     "Ct3": 1.2,           # Transition coefficient
    #     "Ct4": 0.5            # Transition coefficient
    # },

    # `kOmegaCoeffs`: Coefficients for k-omega model
    # "kOmegaCoeffs": {
    #     "beta": 0.075,        # Beta coefficient
    #     "betaStar": 0.09,     # Beta star coefficient
    #     "gamma": 0.52,        # Gamma coefficient
    #     "alphaK": 0.5,        # Alpha coefficient for k equation
    #     "alphaOmega": 0.5     # Alpha coefficient for omega equation
    # },

    # `RNGkEpsilonCoeffs`: Coefficients for RNG k-epsilon model
    # "RNGkEpsilonCoeffs": {
    #     "Cmu": 0.0845,        # Turbulent viscosity coefficient
    #     "C1": 1.42,           # Production coefficient
    #     "C2": 1.68,           # Destruction coefficient
    #     "C3": -0.33,          # Buoyancy coefficient
    #     "sigmak": 0.7194,     # Prandtl number for k
    #     "sigmaEps": 0.7194    # Prandtl number for epsilon
    # }
}

# --- Large Eddy Simulation (LES) Properties ---
# LES resolves the large, energy-containing eddies directly and models the
# smaller ones using sub-grid scale (SGS) models. It is more computationally
# expensive than RAS but provides more detail on transient turbulent structures.

LES_PROPERTIES = {
    # `LESModel`: Specifies the sub-grid scale (SGS) model for LES.
    # This determines how the unresolved small-scale turbulence is modeled.
    # Available Options:
    #   'Smagorinsky': The classic SGS model. Simple and robust but can be
    #                  overly dissipative near walls.
    #   'kEqn': One-equation eddy-viscosity model. Solves an equation for
    #           sub-grid scale kinetic energy. More accurate than Smagorinsky.
    #   'WALE': Wall-Adapting Local Eddy-viscosity model. Better near-wall
    #           behavior than Smagorinsky.
    #   'dynamicKEqn': Dynamic version of kEqn model. Coefficients are
    #                  computed dynamically, more accurate but computationally expensive.
    #   'dynamicSmagorinsky': Dynamic Smagorinsky model. Coefficients computed dynamically.
    #   'SmagorinskyLilly': Lilly's modification of Smagorinsky model.
    #   'SpalartAllmarasDDES': Detached Eddy Simulation variant of Spalart-Allmaras.
    #   'SpalartAllmarasIDDES': Improved Delayed Detached Eddy Simulation.
    #   'kOmegaSSTSAS': k-omega SST with Scale Adaptive Simulation.
    #   'kOmegaSSTDDES': k-omega SST with Detached Eddy Simulation.
    #   'kOmegaSSTIDDES': k-omega SST with Improved Delayed Detached Eddy Simulation.
    #   'oneEqEddy': One-equation eddy viscosity model.
    #   'locDynOneEqEddy': Localized dynamic one-equation eddy viscosity model.
    #   'DeardorffDiffStress': Deardorff differential stress model.
    #   'dynOneEqEddy': Dynamic one-equation eddy viscosity model.
    #   'mixedSmagorinsky': Mixed Smagorinsky model.
    #   'scaleSimilarity': Scale similarity model.
    #   'linearEddy': Linear eddy viscosity model.
    #   'nonlinearEddy': Nonlinear eddy viscosity model.
    #   'Vreman': Vreman SGS model.
    #   'QR': QR SGS model.
    "LESModel": "kEqn",
    
    # `turbulence`: A switch to turn the turbulence calculations on or off.
    # Options: 'on' (LES active), 'off' (laminar simulation)
    "turbulence": "on",

    # `printCoeffs`: Prints the model coefficients to the log file at the start.
    # Options: 'on' (print coefficients), 'off' (don't print)
    "printCoeffs": "on",

    # `delta`: The model for the LES filter width.
    # This determines how the characteristic length scale is calculated.
    # Available Options:
    #   'cubeRootVol': Based on the cell volume. (Most common and recommended)
    #   'vanDriest': Wall-damping model. Reduces filter width near walls.
    #   'smooth': Smoothing for the delta field. Helps with mesh sensitivity.
    #   'maxDeltaxyz': Maximum of x, y, z cell dimensions.
    #   'maxDeltaxy': Maximum of x, y cell dimensions.
    #   'maxDeltaxz': Maximum of x, z cell dimensions.
    #   'maxDeltayz': Maximum of y, z cell dimensions.
    #   'minDeltaxyz': Minimum of x, y, z cell dimensions.
    #   'minDeltaxy': Minimum of x, y cell dimensions.
    #   'minDeltaxz': Minimum of x, z cell dimensions.
    #   'minDeltayz': Minimum of y, z cell dimensions.
    #   'meanDeltaxyz': Mean of x, y, z cell dimensions.
    #   'meanDeltaxy': Mean of x, y cell dimensions.
    #   'meanDeltaxz': Mean of x, z cell dimensions.
    #   'meanDeltayz': Mean of y, z cell dimensions.
    #   'harmonicMeanDeltaxyz': Harmonic mean of x, y, z cell dimensions.
    #   'harmonicMeanDeltaxy': Harmonic mean of x, y cell dimensions.
    #   'harmonicMeanDeltaxz': Harmonic mean of x, z cell dimensions.
    #   'harmonicMeanDeltayz': Harmonic mean of y, z cell dimensions.
    "delta": "smooth",

    # Each delta model and some LES models have their own coefficient sub-dictionaries.
    # The structure below is an example for the kEqn model with smooth delta.

    # `cubeRootVolCoeffs`: Coefficients for cubeRootVol delta model
    "cubeRootVolCoeffs": {
        # `deltaCoeff`: Coefficient for the filter width calculation.
        # Typical range: 0.5 to 2.0. Higher values = larger filter width.
        "deltaCoeff": 1
    },
    
    # `smoothCoeffs`: Coefficients for smooth delta model
    "smoothCoeffs": {
        # `delta`: The base delta model to use for smoothing.
        "delta": "cubeRootVol",
        
        # `cubeRootVolCoeffs`: Coefficients for the base delta model
        "cubeRootVolCoeffs": {
            "deltaCoeff": 1
        },
        
        # `maxDeltaRatio`: Maximum ratio between adjacent delta values.
        # This prevents large jumps in filter width between cells.
        # Typical range: 1.1 to 1.5
        "maxDeltaRatio": 1.1
    },

    # Additional LES model coefficients (advanced users only)
    # `kEqnCoeffs`: Coefficients for kEqn LES model (if using kEqn)
    # "kEqnCoeffs": {
    #     "Ck": 0.094,          # Model coefficient
    #     "Ce": 1.048           # Dissipation coefficient
    # },

    # `SmagorinskyCoeffs`: Coefficients for Smagorinsky model (if using Smagorinsky)
    # "SmagorinskyCoeffs": {
    #     "Ck": 0.094           # Smagorinsky constant
    # },

    # `WALECoeffs`: Coefficients for WALE model (if using WALE)
    # "WALECoeffs": {
    #     "Cw": 0.325           # WALE constant
    # },

    # `dynamicKEqnCoeffs`: Coefficients for dynamic kEqn model
    # "dynamicKEqnCoeffs": {
    #     "Ck": 0.094,          # Model coefficient
    #     "Ce": 1.048,          # Dissipation coefficient
    #     "alpha": 0.09         # Alpha coefficient
    # },

    # `dynamicSmagorinskyCoeffs`: Coefficients for dynamic Smagorinsky model
    # "dynamicSmagorinskyCoeffs": {
    #     "Ck": 0.094,          # Smagorinsky constant
    #     "alpha": 0.09         # Alpha coefficient
    # },

    # `oneEqEddyCoeffs`: Coefficients for one-equation eddy viscosity model
    # "oneEqEddyCoeffs": {
    #     "Ck": 0.094,          # Model coefficient
    #     "Ce": 1.048           # Dissipation coefficient
    # },

    # `VremanCoeffs`: Coefficients for Vreman model
    # "VremanCoeffs": {
    #     "Ck": 0.094           # Model coefficient
    # },

    # `vanDriestCoeffs`: Coefficients for van Driest delta model
    # "vanDriestCoeffs": {
    #     "delta": "cubeRootVol",
    #     "cubeRootVolCoeffs": {
    #         "deltaCoeff": 1
    #     },
    #     "Aplus": 25.0,        # van Driest constant
    #     "Cdelta": 0.158       # Delta coefficient
    # }

    # Add other coefficient dictionaries as needed for your specific model.
}

# --- Laminar Simulation Properties ---
# For flows at low Reynolds numbers where turbulence is not present.
# The dictionary is typically empty as no turbulence modeling is required.

LAMINAR_PROPERTIES = {
    # For laminar flows, no turbulence model coefficients are needed.
    # This dictionary is kept for consistency but should remain empty.
    # If you need to add any laminar-specific parameters in the future,
    # they would go here.
}

# --- Additional Turbulence Settings ---

# `turbulenceOn`: Global switch for turbulence calculations.
# This can be used to quickly disable turbulence for testing.
# Options: True (turbulence active), False (laminar simulation)
turbulenceOn = True

# `turbulenceCorrected`: Enable turbulence corrections for better accuracy.
# This is useful for complex geometries and flow conditions.
# Options: True (enable corrections), False (disable corrections)
turbulenceCorrected = True

# `turbulenceDebug`: Enable debug output for turbulence calculations.
# This provides detailed information about turbulence model behavior.
# Options: True (debug on), False (debug off)
turbulenceDebug = False

# =============================================================================
#           *** Predefined Turbulence Configurations ***
# =============================================================================
# Common turbulence configurations for different simulation types

PREDEFINED_TURBULENCE_CONFIGS = {
    "aerospace_attached": {
        "description": "Aerospace applications with attached flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "SpalartAllmaras",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "aerospace_separated": {
        "description": "Aerospace applications with separated flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "automotive_external": {
        "description": "Automotive external aerodynamics",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "automotive_internal": {
        "description": "Automotive internal flows (engine, HVAC)",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kEpsilon",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "industrial_mixing": {
        "description": "Industrial mixing and chemical processes",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "realizableKE",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "heat_exchanger": {
        "description": "Heat exchanger and thermal systems",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "marine_propeller": {
        "description": "Marine propeller and ship hydrodynamics",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "wind_turbine": {
        "description": "Wind turbine aerodynamics",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "pump_turbine": {
        "description": "Pump and turbine internal flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSST",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "combustion_chamber": {
        "description": "Combustion chamber and burner flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "realizableKE",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "environmental_wind": {
        "description": "Environmental wind and atmospheric flows",
        "simulation_type": "LES",
        "ras_properties": {},
        "les_properties": {
            "LESModel": "kEqn",
            "turbulence": "on",
            "printCoeffs": "on",
            "delta": "cubeRootVol",
            "cubeRootVolCoeffs": {
                "deltaCoeff": 1
            },
        },
        "laminar_properties": {},
    },
    
    "urban_microclimate": {
        "description": "Urban microclimate and building aerodynamics",
        "simulation_type": "LES",
        "ras_properties": {},
        "les_properties": {
            "LESModel": "WALE",
            "turbulence": "on",
            "printCoeffs": "on",
            "delta": "smooth",
            "smoothCoeffs": {
                "delta": "cubeRootVol",
                "cubeRootVolCoeffs": {
                    "deltaCoeff": 1
                },
                "maxDeltaRatio": 1.1
            },
        },
        "laminar_properties": {},
    },
    
    "jet_mixing": {
        "description": "Jet mixing and free shear flows",
        "simulation_type": "LES",
        "ras_properties": {},
        "les_properties": {
            "LESModel": "dynamicKEqn",
            "turbulence": "on",
            "printCoeffs": "on",
            "delta": "cubeRootVol",
            "cubeRootVolCoeffs": {
                "deltaCoeff": 1
            },
        },
        "laminar_properties": {},
    },
    
    "wake_flow": {
        "description": "Wake flows behind obstacles",
        "simulation_type": "LES",
        "ras_properties": {},
        "les_properties": {
            "LESModel": "Smagorinsky",
            "turbulence": "on",
            "printCoeffs": "on",
            "delta": "cubeRootVol",
            "cubeRootVolCoeffs": {
                "deltaCoeff": 1
            },
        },
        "laminar_properties": {},
    },
    
    "transitional_flow": {
        "description": "Laminar-turbulent transition flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSSTLM",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "curved_flow": {
        "description": "Flows with significant streamline curvature",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSSTCC",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "unsteady_separated": {
        "description": "Unsteady separated flows (hybrid RANS/LES)",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "kOmegaSSTSAS",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "detached_eddy": {
        "description": "Detached Eddy Simulation for unsteady flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "SpalartAllmarasDDES",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "improved_detached_eddy": {
        "description": "Improved Delayed Detached Eddy Simulation",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "SpalartAllmarasIDDES",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "low_reynolds": {
        "description": "Low Reynolds number flows",
        "simulation_type": "RAS",
        "ras_properties": {
            "RASModel": "LienLeschzinerLowRe",
            "turbulence": "on",
            "printCoeffs": "on",
        },
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "laminar_flow": {
        "description": "Laminar flow simulation",
        "simulation_type": "laminar",
        "ras_properties": {},
        "les_properties": {},
        "laminar_properties": {},
    },
    
    "high_accuracy_les": {
        "description": "High accuracy LES for research",
        "simulation_type": "LES",
        "ras_properties": {},
        "les_properties": {
            "LESModel": "dynamicKEqn",
            "turbulence": "on",
            "printCoeffs": "on",
            "delta": "vanDriest",
            "vanDriestCoeffs": {
                "delta": "cubeRootVol",
                "cubeRootVolCoeffs": {
                    "deltaCoeff": 1
                },
                "Aplus": 25.0,
                "Cdelta": 0.158
            },
        },
        "laminar_properties": {},
    },
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined turbulence configuration to use (overrides manual settings above)

USE_PREDEFINED_TURBULENCE = None  # Set to turbulence config name from PREDEFINED_TURBULENCE_CONFIGS or None for manual config

# Example usage:
# USE_PREDEFINED_TURBULENCE = "aerospace_attached"  # Will use Spalart-Allmaras for aerospace
# USE_PREDEFINED_TURBULENCE = "automotive_external"  # Will use k-omega SST for automotive
# USE_PREDEFINED_TURBULENCE = "environmental_wind"   # Will use LES for environmental flows