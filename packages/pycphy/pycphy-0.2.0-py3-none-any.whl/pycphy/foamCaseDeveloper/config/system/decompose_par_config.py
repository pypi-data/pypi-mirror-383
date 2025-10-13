# decompose_par_config.py

"""
Decompose Par Configuration for OpenFOAM cases.

This module provides configuration options for the decomposePar utility to
decompose mesh and fields for parallel processing including various
decomposition methods and load balancing strategies.
"""

# =============================================================================
#           *** User Input for decomposeParDict ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'system/decomposeParDict'.
WRITE_DECOMPOSE_PAR_DICT = True

# =============================================================================
#           *** Decomposition Configuration ***
# =============================================================================

DECOMPOSE_PAR_CONFIG = {
    # Number of domains to decompose into
    # Must match the number of processors you want to use
    "numberOfSubdomains": 4,
    
    # Decomposition method
    # Options:
    #   "simple": Simple geometric decomposition (fastest)
    #   "hierarchical": Hierarchical decomposition (good for structured meshes)
    #   "scotch": Scotch decomposition (good load balancing)
    #   "metis": METIS decomposition (good load balancing)
    #   "manual": Manual decomposition (user-specified)
    #   "multiLevel": Multi-level decomposition (for complex geometries)
    #   "structured": Structured decomposition (for structured meshes)
    #   "kahip": KaHIP decomposition (advanced load balancing)
    #   "ptscotch": PT-Scotch decomposition (parallel Scotch)
    "method": "scotch",
    
    # Decomposition coefficients (method-specific)
    "coeffs": {
        # For 'simple' method
        "simpleCoeffs": {
            "n": (2, 2, 1),  # Number of domains in x, y, z directions
            "delta": 0.001,  # Cell skewness factor
        },
        
        # For 'hierarchical' method
        "hierarchicalCoeffs": {
            "n": (2, 2, 1),  # Number of domains in x, y, z directions
            "delta": 0.001,  # Cell skewness factor
            "order": "xyz",  # Decomposition order
        },
        
        # For 'scotch' method
        "scotchCoeffs": {
            "strategy": "b",  # Scotch strategy (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z)
            "processorWeights": [1, 1, 1, 1],  # Relative processor weights
        },
        
        # For 'metis' method
        "metisCoeffs": {
            "processorWeights": [1, 1, 1, 1],  # Relative processor weights
        },
        
        # For 'manual' method
        "manualCoeffs": {
            "dataFile": "manualDecompData",  # File containing manual decomposition data
        },
        
        # For 'multiLevel' method
        "multiLevelCoeffs": {
            "method": "scotch",
            "coeffs": {
                "strategy": "b",
            },
            "multiLevelCoeffs": {
                "method": "simple",
                "coeffs": {
                    "n": (2, 2, 1),
                },
            },
        },
        
        # For 'structured' method
        "structuredCoeffs": {
            "patches": ["inlet", "outlet"],  # Patches to preserve
            "n": (2, 2, 1),  # Number of domains in x, y, z directions
        },
        
        # For 'kahip' method
        "kahipCoeffs": {
            "config": "fast",  # KaHIP configuration (fast, eco, strong)
            "seed": 0,  # Random seed
        },
        
        # For 'ptscotch' method
        "ptscotchCoeffs": {
            "strategy": "b",  # PT-Scotch strategy
            "processorWeights": [1, 1, 1, 1],  # Relative processor weights
        },
    },
    
    # Additional decomposition options
    "options": {
        # Write decomposition information
        "writeGraph": True,
        
        # Write processor weights
        "writeProcWeights": True,
        
        # Write cell distribution
        "writeCellDist": True,
        
        # Write face distribution
        "writeFaceDist": True,
        
        # Write point distribution
        "writePointDist": True,
        
        # Write decomposition statistics
        "writeStats": True,
        
        # Write decomposition quality metrics
        "writeQuality": True,
        
        # Write decomposition visualization
        "writeVTK": True,
        
        # Write decomposition log
        "writeLog": True,
        
        # Verbose output
        "verbose": True,
        
        # Check decomposition
        "checkDecomp": True,
        
        # Reconstruct decomposition
        "reconstruct": False,
        
        # Force decomposition
        "force": False,
        
        # Keep original mesh
        "keepOriginal": True,
        
        # Backup original files
        "backup": True,
        
        # Compress output
        "compress": False,
        
        # Use parallel decomposition
        "parallel": True,
        
        # Number of threads for parallel decomposition
        "nThreads": 4,
        
        # Memory limit for decomposition
        "memoryLimit": "2GB",
        
        # Time limit for decomposition
        "timeLimit": "3600",  # 1 hour
    },
    
    # Fields to decompose
    "fields": [
        "U",      # Velocity field
        "p",      # Pressure field
        "T",      # Temperature field (if present)
        "k",      # Turbulent kinetic energy (if present)
        "epsilon", # Turbulent dissipation rate (if present)
        "omega",  # Specific dissipation rate (if present)
        "nuTilda", # Spalart-Allmaras variable (if present)
        "alpha.water", # Volume fraction (if present)
        "rho",    # Density (if present)
        "mu",     # Dynamic viscosity (if present)
        "phi",    # Flux field
        "phi_0",  # Flux field (alternative)
        "phi_1",  # Flux field (alternative)
        "phi_2",  # Flux field (alternative)
        "phi_3",  # Flux field (alternative)
    ],
    
    # Patches to preserve during decomposition
    "preservePatches": [
        "inlet",
        "outlet",
        "wall",
        "symmetry",
        "cyclic",
        "processor",
    ],
    
    # Cell zones to preserve during decomposition
    "preserveCellZones": [
        "porousZone",
        "sourceZone",
        "sinkZone",
    ],
    
    # Face zones to preserve during decomposition
    "preserveFaceZones": [
        "interface",
        "contact",
    ],
    
    # Point zones to preserve during decomposition
    "preservePointZones": [
        "inletPoints",
        "outletPoints",
    ],
}

# =============================================================================
#           *** Predefined Decomposition Configurations ***
# =============================================================================
# Common decomposition configurations for different scenarios

PREDEFINED_DECOMPOSITION_CONFIGS = {
    "small_problem": {
        "description": "Small problem decomposition (2-4 processors)",
        "numberOfSubdomains": 2,
        "method": "simple",
        "coeffs": {
            "simpleCoeffs": {
                "n": (2, 1, 1),
                "delta": 0.001,
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": False,
        },
    },
    
    "medium_problem": {
        "description": "Medium problem decomposition (4-8 processors)",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
            "nThreads": 2,
        },
    },
    
    "large_problem": {
        "description": "Large problem decomposition (8-16 processors)",
        "numberOfSubdomains": 8,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1, 1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
            "nThreads": 4,
            "memoryLimit": "4GB",
        },
    },
    
    "huge_problem": {
        "description": "Huge problem decomposition (16+ processors)",
        "numberOfSubdomains": 16,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1] * 16,
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
            "nThreads": 8,
            "memoryLimit": "8GB",
            "timeLimit": "7200",  # 2 hours
        },
    },
    
    "structured_mesh": {
        "description": "Decomposition for structured meshes",
        "numberOfSubdomains": 4,
        "method": "structured",
        "coeffs": {
            "structuredCoeffs": {
                "patches": ["inlet", "outlet", "wall"],
                "n": (2, 2, 1),
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
    },
    
    "unstructured_mesh": {
        "description": "Decomposition for unstructured meshes",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
    },
    
    "multiphase_flow": {
        "description": "Decomposition for multiphase flow simulations",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
            "writeVTK": True,
        },
        "fields": [
            "U", "p", "alpha.water", "phi", "phi_0", "phi_1", "phi_2", "phi_3",
        ],
    },
    
    "turbulent_flow": {
        "description": "Decomposition for turbulent flow simulations",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
        "fields": [
            "U", "p", "k", "epsilon", "phi", "phi_0", "phi_1", "phi_2", "phi_3",
        ],
    },
    
    "heat_transfer": {
        "description": "Decomposition for heat transfer simulations",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
        "fields": [
            "U", "p", "T", "phi", "phi_0", "phi_1", "phi_2", "phi_3",
        ],
    },
    
    "compressible_flow": {
        "description": "Decomposition for compressible flow simulations",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
        "fields": [
            "U", "p", "T", "rho", "mu", "phi", "phi_0", "phi_1", "phi_2", "phi_3",
        ],
    },
    
    "species_transport": {
        "description": "Decomposition for species transport simulations",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "verbose": True,
            "parallel": True,
        },
        "fields": [
            "U", "p", "Y_CO2", "Y_O2", "Y_N2", "phi", "phi_0", "phi_1", "phi_2", "phi_3",
        ],
    },
    
    "high_performance": {
        "description": "High-performance decomposition with advanced options",
        "numberOfSubdomains": 8,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1, 1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": True,
            "writeProcWeights": True,
            "writeCellDist": True,
            "writeFaceDist": True,
            "writePointDist": True,
            "writeStats": True,
            "writeQuality": True,
            "writeVTK": True,
            "writeLog": True,
            "verbose": True,
            "checkDecomp": True,
            "parallel": True,
            "nThreads": 8,
            "memoryLimit": "8GB",
            "timeLimit": "3600",
        },
    },
    
    "debug_mode": {
        "description": "Debug mode decomposition with extensive output",
        "numberOfSubdomains": 2,
        "method": "simple",
        "coeffs": {
            "simpleCoeffs": {
                "n": (2, 1, 1),
                "delta": 0.001,
            },
        },
        "options": {
            "writeGraph": True,
            "writeProcWeights": True,
            "writeCellDist": True,
            "writeFaceDist": True,
            "writePointDist": True,
            "writeStats": True,
            "writeQuality": True,
            "writeVTK": True,
            "writeLog": True,
            "verbose": True,
            "checkDecomp": True,
            "parallel": False,
        },
    },
    
    "production_mode": {
        "description": "Production mode decomposition optimized for performance",
        "numberOfSubdomains": 4,
        "method": "scotch",
        "coeffs": {
            "scotchCoeffs": {
                "strategy": "b",
                "processorWeights": [1, 1, 1, 1],
            },
        },
        "options": {
            "writeGraph": False,
            "writeProcWeights": False,
            "writeCellDist": False,
            "writeFaceDist": False,
            "writePointDist": False,
            "writeStats": False,
            "writeQuality": False,
            "writeVTK": False,
            "writeLog": False,
            "verbose": False,
            "checkDecomp": False,
            "parallel": True,
            "nThreads": 4,
            "compress": True,
        },
    },
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined decomposition configuration to use (overrides manual settings above)

USE_PREDEFINED_DECOMPOSITION = None  # Set to decomposition config name from PREDEFINED_DECOMPOSITION_CONFIGS or None for manual config

# Example usage:
# USE_PREDEFINED_DECOMPOSITION = "medium_problem"  # Will use medium problem decomposition
# USE_PREDEFINED_DECOMPOSITION = "multiphase_flow"  # Will use multiphase flow decomposition
