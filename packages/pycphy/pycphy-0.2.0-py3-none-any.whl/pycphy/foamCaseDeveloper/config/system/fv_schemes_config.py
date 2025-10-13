# fv_schemes_config.py

"""
Finite Volume Schemes Configuration for OpenFOAM cases.

This module provides comprehensive configuration options for finite volume discretization
schemes including time derivatives, gradients, divergence, Laplacian, interpolation,
and surface normal gradients.
"""

# =============================================================================
#           *** User Input for fvSchemes ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'system/fvSchemes'.
WRITE_FV_SCHEMES = True

# =============================================================================
#           *** Time Derivative Schemes (ddtSchemes) ***
# =============================================================================
# Control how time derivatives are discretized

DDT_SCHEMES = {
    # Default scheme for all time derivatives
    # Options:
    #   "Euler": First-order explicit Euler (unconditionally unstable)
    #   "backward": First-order implicit backward Euler (unconditionally stable)
    #   "CrankNicolson": Second-order implicit Crank-Nicolson (conditionally stable)
    #   "localEuler": Local time stepping with Euler scheme
    #   "steadyState": For steady-state simulations (no time derivative)
    #   "localSteadyState": Local steady-state (useful for initialization)
    "default": "backward",
    
    # Field-specific schemes (optional)
    "fieldSpecific": {
        # Example: Use different scheme for specific fields
        # "p": "Gauss linear",
        # "U": "Gauss upwind",
    }
}

# =============================================================================
#           *** Gradient Schemes (gradSchemes) ***
# =============================================================================
# Control how gradients are computed

GRAD_SCHEMES = {
    # Default gradient scheme
    # Options:
    #   "Gauss linear": Second-order accurate central difference
    #   "Gauss linearUpwind": First-order upwind (stable but diffusive)
    #   "Gauss linearUpwind grad": Upwind with gradient correction
    #   "Gauss pointCellsLeastSquares": Least squares gradient
    #   "Gauss cellMDLimited": Cell-based multi-dimensional limiter
    #   "Gauss faceMDLimited": Face-based multi-dimensional limiter
    #   "leastSquares": Least squares gradient (alternative syntax)
    "default": "Gauss linear",
    
    # Field-specific gradient schemes
    "fieldSpecific": {
        # Example: Use different gradient schemes for different fields
        "p": "Gauss linear",           # Pressure gradient
        "U": "Gauss linear",           # Velocity gradient
        # "T": "Gauss linearUpwind",   # Temperature gradient (upwind for stability)
        # "k": "Gauss linearUpwind",   # Turbulent kinetic energy (upwind)
        # "epsilon": "Gauss linearUpwind",  # Turbulent dissipation rate (upwind)
    }
}

# =============================================================================
#           *** Divergence Schemes (divSchemes) ***
# =============================================================================
# Control how divergence terms are discretized

DIV_SCHEMES = {
    # Default divergence scheme
    "default": "none",
    
    # Field-specific divergence schemes
    "fieldSpecific": {
        # Convection terms (phi is the flux)
        "div(phi,U)": "Gauss linear",                    # Momentum convection
        "div(phi,k)": "Gauss upwind",                    # Turbulent kinetic energy convection
        "div(phi,epsilon)": "Gauss upwind",              # Turbulent dissipation convection
        "div(phi,omega)": "Gauss upwind",                # Specific dissipation rate convection
        "div(phi,T)": "Gauss linear",                    # Temperature convection
        "div(phi,Yi)": "Gauss upwind",                   # Species mass fraction convection
        "div(phi,alpha.water)": "Gauss vanLeer",         # Volume fraction convection (VOF)
        
        # Diffusion terms
        "div((nuEff*dev2(T(grad(U)))))": "Gauss linear", # Viscous stress divergence
        "div((nuEff*dev(T(grad(U)))))": "Gauss linear",  # Viscous stress divergence (alternative)
        "div((alpha*he*U))": "Gauss linear",             # Enthalpy convection
        "div((rho*U))": "Gauss linear",                  # Mass convection
        "div((rho*U*U))": "Gauss linear",                # Momentum convection
        "div((rho*phi*U))": "Gauss linear",              # Momentum convection with phi
        
        # Turbulent terms
        "div(phi,nuTilda)": "Gauss upwind",              # Spalart-Allmaras convection
        "div(phi,R)": "Gauss linear",                    # Reynolds stress convection
        
        # Compressible flow terms
        "div(phi,p)": "Gauss linear",                    # Pressure convection
        "div(phi,h)": "Gauss linear",                    # Enthalpy convection
        "div(phi,rho)": "Gauss linear",                  # Density convection
        
        # Multiphase flow terms
        "div(phi,alpha1)": "Gauss vanLeer",              # Phase fraction convection
        "div(phi,alpha2)": "Gauss vanLeer",              # Phase fraction convection
        "div(phi,alpha)": "Gauss vanLeer",               # Volume fraction convection
        
        # Combustion terms
        "div(phi,Yi)": "Gauss upwind",                   # Species mass fraction
        "div(phi,Y)": "Gauss upwind",                    # Mass fraction (generic)
        "div(phi,ft)": "Gauss upwind",                   # Mixture fraction
        "div(phi,Z)": "Gauss upwind",                    # Progress variable
    }
}

# =============================================================================
#           *** Laplacian Schemes (laplacianSchemes) ***
# =============================================================================
# Control how Laplacian (diffusion) terms are discretized

LAPLACIAN_SCHEMES = {
    # Default Laplacian scheme
    # Options:
    #   "Gauss linear": Second-order central difference
    #   "Gauss linear corrected": Corrected for non-orthogonal meshes
    #   "Gauss linear limited": Limited to prevent overshoots
    #   "Gauss linear limited corrected": Limited and corrected
    #   "Gauss linear uncorrected": Uncorrected (faster but less accurate)
    #   "Gauss linear orthogonal": For orthogonal meshes only
    "default": "Gauss linear corrected",
    
    # Field-specific Laplacian schemes
    "fieldSpecific": {
        # Diffusion terms
        "laplacian(nu,U)": "Gauss linear corrected",     # Viscous diffusion
        "laplacian(nuEff,U)": "Gauss linear corrected",  # Effective viscous diffusion
        "laplacian(DT,T)": "Gauss linear corrected",     # Thermal diffusion
        "laplacian(DT,h)": "Gauss linear corrected",     # Enthalpy diffusion
        "laplacian(D,Yi)": "Gauss linear corrected",     # Species diffusion
        "laplacian(alpha,rho)": "Gauss linear corrected", # Density diffusion
        "laplacian(1,p)": "Gauss linear corrected",      # Pressure diffusion (Poisson)
        "laplacian(1,rho)": "Gauss linear corrected",    # Density diffusion
        
        # Turbulent diffusion
        "laplacian(nuTilda,nuTilda)": "Gauss linear corrected",  # Spalart-Allmaras
        "laplacian((nu+nuT),U)": "Gauss linear corrected",       # Turbulent viscosity
        
        # Multiphase diffusion
        "laplacian(alpha,alpha)": "Gauss linear corrected",      # Phase fraction diffusion
        "laplacian(D32,alpha)": "Gauss linear corrected",        # Phase fraction diffusion
    }
}

# =============================================================================
#           *** Interpolation Schemes (interpolationSchemes) ***
# =============================================================================
# Control how values are interpolated from cell centers to face centers

INTERPOLATION_SCHEMES = {
    # Default interpolation scheme
    # Options:
    #   "linear": Second-order linear interpolation
    #   "linearUpwind": First-order upwind (stable but diffusive)
    #   "skewCorrected linear": Skewness-corrected linear
    #   "cubic": Third-order cubic interpolation
    #   "upwind": First-order upwind
    #   "midPoint": Mid-point interpolation (first-order)
    #   "harmonic": Harmonic mean interpolation
    #   "pointCellsLeastSquares": Least squares interpolation
    "default": "linear",
    
    # Field-specific interpolation schemes
    "fieldSpecific": {
        # Example: Use different interpolation for different fields
        # "U": "linear",                    # Velocity interpolation
        # "p": "linear",                    # Pressure interpolation
        # "T": "linearUpwind",              # Temperature interpolation (upwind for stability)
        # "alpha.water": "linear",          # Volume fraction interpolation
    }
}

# =============================================================================
#           *** Surface Normal Gradient Schemes (snGradSchemes) ***
# =============================================================================
# Control how surface normal gradients are computed

SNGRAD_SCHEMES = {
    # Default surface normal gradient scheme
    # Options:
    #   "corrected": Corrected for non-orthogonal meshes (recommended)
    #   "uncorrected": Uncorrected (faster but less accurate on non-orthogonal meshes)
    #   "limited": Limited to prevent overshoots
    #   "orthogonal": For orthogonal meshes only
    #   "limited corrected": Limited and corrected
    "default": "corrected",
    
    # Field-specific surface normal gradient schemes
    "fieldSpecific": {
        # Example: Use different schemes for different fields
        # "p": "corrected",                 # Pressure gradient
        # "U": "corrected",                 # Velocity gradient
        # "T": "corrected",                 # Temperature gradient
    }
}

# =============================================================================
#           *** Flux Required Schemes (fluxRequired) ***
# =============================================================================
# Specify which fields require flux computation

FLUX_REQUIRED_SCHEMES = {
    # Enable flux computation for specific fields
    "enabled": True,
    
    # List of fields that require flux computation
    "fields": [
        "p",                    # Pressure field
        "U",                    # Velocity field
        "T",                    # Temperature field
        # "alpha.water",        # Volume fraction field
        # "k",                  # Turbulent kinetic energy
        # "epsilon",            # Turbulent dissipation rate
        # "omega",              # Specific dissipation rate
        # "nuTilda",            # Spalart-Allmaras variable
    ]
}

# =============================================================================
#           *** Predefined Scheme Sets ***
# =============================================================================
# Common scheme configurations for different simulation types

PREDEFINED_SCHEME_SETS = {
    "laminar_steady": {
        "description": "Laminar steady-state simulation",
        "ddtSchemes": {"default": "steadyState"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linear"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "laminar_transient": {
        "description": "Laminar transient simulation",
        "ddtSchemes": {"default": "backward"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linear"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "turbulent_ras": {
        "description": "Reynolds-Averaged Navier-Stokes (RANS) simulation",
        "ddtSchemes": {"default": "backward"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
                "div(phi,k)": "Gauss upwind",
                "div(phi,epsilon)": "Gauss upwind",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linear"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "turbulent_les": {
        "description": "Large Eddy Simulation (LES)",
        "ddtSchemes": {"default": "backward"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linear"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "multiphase_vof": {
        "description": "Multiphase Volume of Fluid (VOF) simulation",
        "ddtSchemes": {"default": "backward"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
                "div(phi,alpha.water)": "Gauss vanLeer",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linear"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "high_order": {
        "description": "High-order accurate schemes (for smooth flows)",
        "ddtSchemes": {"default": "CrankNicolson"},
        "gradSchemes": {"default": "Gauss linear"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss linear",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "cubic"},
        "snGradSchemes": {"default": "corrected"},
    },
    
    "stable_upwind": {
        "description": "Stable upwind schemes (for difficult flows)",
        "ddtSchemes": {"default": "backward"},
        "gradSchemes": {"default": "Gauss linearUpwind"},
        "divSchemes": {
            "default": "none",
            "fieldSpecific": {
                "div(phi,U)": "Gauss upwind",
                "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
            }
        },
        "laplacianSchemes": {"default": "Gauss linear corrected"},
        "interpolationSchemes": {"default": "linearUpwind"},
        "snGradSchemes": {"default": "corrected"},
    }
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined scheme set to use (overrides manual settings above)

USE_PREDEFINED_SCHEMES = None  # Set to scheme set name from PREDEFINED_SCHEME_SETS or None for manual config

# Example usage:
# USE_PREDEFINED_SCHEMES = "turbulent_ras"  # Will use RANS-appropriate schemes
