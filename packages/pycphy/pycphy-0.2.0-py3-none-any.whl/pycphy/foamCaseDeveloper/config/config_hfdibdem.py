# config_hfdibdem.py

# =============================================================================
#           *** User Input for HFDIBDEMDict ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'constant/HFDIBDEMDict'.
WRITE_HFDIBDEM_DICT = True


# =============================================================================
# --- 1. Global Simulation Settings ---
# =============================================================================
GLOBAL_SETTINGS = {
    # `interpolationSchemes`: How fields are interpolated from mesh to IB points.
    "interpolationSchemes": {
        "U": "cell",         # Options: 'cell', 'cellPointFace'
        # "method": "line"   # Optional, for some schemes
    },

    # `surfaceThreshold`: VOF value defining the fluid/solid interface.
    "surfaceThreshold": 1e-4,

    # `stepDEM`: Time step for the DEM solver. Usually smaller than fluid deltaT.
    "stepDEM": 0.01,

    # `geometricD`: Directions considered for collision (1=active, 0=ignore, -1=2D).
    # e.g., (1 1 -1) for a 2D simulation in XY plane.
    "geometricD": (1, 1, 1),

    # `recordSimulation`: Master switch to save IB/DEM data.
    "recordSimulation": True,
    "recordFirstTimeStep": False,

    # `nSolidsInDomain`: Max limit on particles. Optional, defaults to 1000 if omitted.
    "nSolidsInDomain": 5000,

    # `outputSetup`: Fine-grained control over what data is written.
    "outputSetup": {
        "basic": False,
        "iB": False,        # Immersed Boundary data
        "DEM": False,       # Discrete Element Method data
        "addModel": False,  # Particle insertion data
        "parallelDEM": False
    }
}

# `virtualMesh`: Settings for the background mesh used for particle tracking.
VIRTUAL_MESH_SETTINGS = {
    "level": 4,                 # Refinement level of the virtual mesh.
    "charCellSize": 0.001,      # Characteristic cell size.
    "recordContact": False      # Record particle-particle/wall contacts.
}


# =============================================================================
# --- 2. DEM Physics & Environment ---
# =============================================================================
DEM_SETTINGS = {
    "LcCoeff": 4.0, # Collision length scale coefficient.
    
    # Optional rotation model (e.g., 'chen2012', 'mindlin1953'). Uncomment to use.
    # "rotationModel": "chen2012", 

    # `materials`: Material properties for particles and walls.
    "materials": {
        "particleMat1": {
            "Y": 5e8,       # Young's Modulus (Pa)
            "nu": 0.5,      # Poisson's Ratio
            "mu": 1.0,      # Friction Coefficient
            "adhN": 0,      # Normal Adhesion Energy
            "eps": 0.75     # Coefficient of Restitution
        },
        "wallMat": {
            "Y": 1e10, "nu": 0.5, "mu": 1.0, "adhN": 0, "eps": 0.75
        }
    },

    # `collisionPatches`: planar walls defined by normal & point.
    "collisionPatches": {
        "floor": {
            "material": "wallMat", # Must match a name in 'materials'
            "nVec": (0, 1.0, 0),   # Normal vector pointing INTO domain
            "planePoint": (0, 0, 0)
        },
        # Add more walls as needed (e.g., ceiling, side walls)
        # "ceiling": { ... }
    },
    
    # `cyclicPatches`: For periodic boundaries in DEM.
    "cyclicPatches": {
        # "outlet": {
        #     "material": "wallMat",
        #     "nVec": (0, -1, 0),
        #     "planePoint": (0, -0.1, 0),
        #     "neighbourPatch": "inlet"
        # },
        # "inlet": { ... neighbourPatch "outlet" ... }
    }
}


# =============================================================================
# --- 3. Body Definitions (The "Library" of Bodies) ---
# =============================================================================
# Define all potential bodies here. You select which ones to use below.
AVAILABLE_BODIES = {
    # --- Example A: A single falling sphere ---
    "singleFallingSphere": {
        # Body Type: 'fullyCoupledBody', 'staticBody', 'prescribedTransRotBody'
        "fullyCoupledBody": {
            "velocity": (0, -1.0, 0) # Initial velocity
        },
        
        # Properties with units defined explicitly in the string
        "rho": "rho [1 -3 0 0 0 0 0] 2500", # Density kg/m^3
        "refineMC": 5,                      # Marching Cubes refinement
        "U": {"BC": "noSlip"},              # Boundary Condition on body surface
        "material": "particleMat1",         # Link to DEM.materials
        "updateTorque": True,

        # Geometry definition
        "bodyGeom": "sphere", # 'sphere', 'convex', 'nonConvex'
        "sphere": {
            "radius": 0.04,
            "startPosition": (0, 0.2, 0)
        },

        # Particle insertion model
        "bodyAddition": {
            "addModel": "once", # 'once', 'onceScatter', 'distribution'
            "onceCoeffs": {}    # No extra coeffs for simple 'once'
        },
        
        "timesToSetStatic": -1 # -1 = never become static
    },

    # --- Example B: A cloud of particles ("onceScatter") ---
    "particleCloud": {
        "fullyCoupledBody": {}, # Zero initial velocity
        "rho": "rho [1 -3 0 0 0 0 0] 4000",
        "material": "particleMat1",
        
        # For complex shapes read from STL (implied by nonConvex/convex)
        "bodyGeom": "convex", 

        "bodyAddition": {
            "addModel": "onceScatter",
            "onceScatterCoeffs": {
                "addMode": "fieldBased", # Insert based on a field value (e.g. VOF)
                "fieldBasedCoeffs": {
                    "fieldName": "lambda", # The field name
                    "fieldValue": 0.3      # Threshold value
                },
                "addDomain": "boundBox",   # Region to insert into
                "boundBoxCoeffs": {
                    "minBound": (-0.1, 0.0, -0.1),
                    "maxBound": ( 0.1, 0.5,  0.1)
                },
                "scalingMode": "noScaling", "noScalingCoeffs": {},
                "rotationMode": "randomRotation", "randomRotationCoeffs": {}
            }
        },
        "nParticles": 500, # Optional hint, sometimes used by the solver
        "timesToSetStatic": 1500 # Become static after this many steps
    },
    
    # --- Example C: A prescribed motion rotor ---
    "rotor": {
        "prescribedTransRotBody": {
            "velocity": (0,0,0),
            "axis": (0, 1, 0), # Y-axis rotation
            "omega": 50.0      # Rad/s
        },
        "rho": "rho [1 -3 0 0 0 0 0] 1000",
        "material": "wallMat", # Acts like a moving wall
        "bodyGeom": "nonConvex", # Read from STL (e.g., rotor.stl)
        "bodyAddition": { "addModel": "once", "onceCoeffs": {} }
    }
}


# =============================================================================
# --- 4. Case Selection ---
# =============================================================================
# Select which bodies from AVAILABLE_BODIES to include in this simulation.
# The names here MUST exist as keys in the AVAILABLE_BODIES dictionary above.
SELECTED_BODY_NAMES = [
    "singleFallingSphere",
    # "particleCloud",
    # "rotor"
]