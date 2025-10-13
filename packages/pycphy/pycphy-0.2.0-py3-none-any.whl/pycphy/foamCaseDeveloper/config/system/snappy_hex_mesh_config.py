# snappy_hex_mesh_config.py

# =============================================================================
#           *** User Input for snappyHexMeshDict ***
# =============================================================================
#
#   This file defines the mesh generation parameters for snappyHexMesh.
#   snappyHexMesh is used for complex geometry meshing with automatic
#   boundary layer generation and mesh refinement.
#

# `WRITE_SNAPPY_HEX_MESH_DICT`: Set to True to enable writing of the snappyHexMeshDict file.
# If False, this component will be skipped.
WRITE_SNAPPY_HEX_MESH_DICT = True

# --- Step Control ---
# Which steps of snappyHexMesh to run
CASTELLATED_MESH = True  # Initial mesh generation and refinement
SNAP = True            # Snap mesh to geometry surfaces
ADD_LAYERS = False     # Add boundary layers (can be computationally expensive)

# --- Geometry Definition ---
# `GEOMETRY`: Dictionary containing all geometry files and analytical shapes.
# Each entry maps a geometry name to its definition.
# Supports both STL/OBJ files and analytical shapes (box, sphere, cylinder, etc.)
GEOMETRY = {
    # Surface mesh files (STL, OBJ, etc.)
    "motorBike": {
        "type": "triSurfaceMesh",
        "file": "motorBike.obj"
    },
    
    # Analytical shapes for refinement regions
    "refinementBox": {
        "type": "box",
        "min": [-1.0, -0.7, 0.0],
        "max": [8.0, 0.7, 2.5]
    },
    
    # Example of cylinder for pipe flows
    # "pipe": {
    #     "type": "cylinder",
    #     "point1": [0, 0, 0],
    #     "point2": [0, 0, 1],
    #     "radius": 0.1
    # },
    
    # Example of sphere for bluff body flows
    # "sphere": {
    #     "type": "sphere",
    #     "centre": [0, 0, 0],
    #     "radius": 0.05
    # }
}

# --- Castellated Mesh Controls ---
# `CASTELLATED_MESH_CONTROLS`: Controls for the initial mesh generation phase.
CASTELLATED_MESH_CONTROLS = {
    # Refinement parameters
    "maxLocalCells": 100000,      # Max cells per processor before balancing
    "maxGlobalCells": 8000000,    # Total cell limit (approximate)
    "minRefinementCells": 10,     # Stop if fewer cells selected for refinement
    "maxLoadUnbalance": 0.10,     # Allow imbalance during refinement (0=perfect balance)
    "nCellsBetweenLevels": 3,     # Buffer layers between refinement levels
    
    # Feature edge refinement (from .eMesh files)
    "features": [
        {
            "file": "motorBike.eMesh",
            "level": 7  # Refinement level for feature edges
        }
    ],
    
    # Surface-based refinement
    "refinementSurfaces": {
        "motorBike": {
            "level": (7, 7),  # (minLevel, maxLevel) for surface refinement
            "patchInfo": {
                "type": "wall",
                "inGroups": ["motorBikeGroup"]
            }
        }
    },
    
    # Sharp angle resolution
    "resolveFeatureAngle": 30,  # Degrees - resolve angles sharper than this
    
    # Region-wise refinement (distance-based, inside, or outside)
    "refinementRegions": {
        "refinementBox": {
            "mode": "inside",
            "levels": ((1e15, 4))  # (distance, level) pairs
        }
    },
    
    # Mesh selection point (must be inside the domain)
    "locationInMesh": [3.0001, 3.0001, 0.43],
    
    # Zone face handling
    "allowFreeStandingZoneFaces": True
}

# --- Snap Controls ---
# `SNAP_CONTROLS`: Controls for the mesh snapping phase to geometry.
SNAP_CONTROLS = {
    # Patch smoothing iterations before surface correspondence
    "nSmoothPatch": 3,
    
    # Relative distance for surface feature attraction
    "tolerance": 2.0,
    
    # Mesh displacement relaxation iterations
    "nSolveIter": 30,
    
    # Maximum snapping relaxation iterations
    "nRelaxIter": 5,
    
    # Feature snapping iterations
    "nFeatureSnapIter": 10,
    
    # Feature detection methods
    "implicitFeatureSnap": False,    # Detect features by surface sampling
    "explicitFeatureSnap": True,     # Use features from castellatedMeshControls
    "multiRegionFeatureSnap": False  # Detect points on multiple surfaces
}

# --- Add Layers Controls ---
# `ADD_LAYERS_CONTROLS`: Controls for boundary layer generation.
ADD_LAYERS_CONTROLS = {
    # Thickness parameters relative to cell size outside layer
    "relativeSizes": True,
    
    # Layer definitions per patch (using regex patterns)
    "layers": {
        "(lowerWall|motorBike).*": {
            "nSurfaceLayers": 1  # Number of boundary layers
        }
    },
    
    # Layer expansion ratio (thickness growth)
    "expansionRatio": 1.0,
    
    # Final layer thickness (relative to cell size)
    "finalLayerThickness": 0.3,
    
    # Minimum layer thickness
    "minThickness": 0.1,
    
    # Connected face growth for convergence
    "nGrow": 0,
    
    # Advanced settings
    "featureAngle": 60,                    # Angle threshold for layer termination
    "nRelaxIter": 5,                      # Relaxation iterations
    "nSmoothSurfaceNormals": 1,           # Surface normal smoothing
    "nSmoothNormals": 3,                  # Normal smoothing iterations
    "nSmoothThickness": 10,               # Thickness smoothing iterations
    "maxFaceThicknessRatio": 0.5,         # Max face thickness ratio
    "maxThicknessToMedialRatio": 0.3,     # Max thickness to medial ratio
    "minMedianAxisAngle": 90,             # Min median axis angle
    "nBufferCellsNoExtrude": 0,           # Buffer cells without extrusion
    "nLayerIter": 50,                     # Layer addition iterations
    "nRelaxedIter": 20                    # Relaxed iterations
}

# --- Mesh Quality Controls ---
# `MESH_QUALITY_CONTROLS`: Controls for mesh quality optimization.
MESH_QUALITY_CONTROLS = {
    # Orthogonality and skewness
    "maxNonOrtho": 65,              # Maximum non-orthogonality
    "maxBoundarySkewness": 20,      # Maximum boundary face skewness
    "maxInternalSkewness": 4,       # Maximum internal face skewness
    "maxConcave": 80,               # Maximum concavity
    
    # Volume and area constraints
    "minFlatness": 0.5,             # Minimum face flatness
    "minVol": 1e-13,                # Minimum cell volume
    "minTetQuality": 1e-30,         # Minimum tetrahedron quality
    "minArea": -1,                  # Minimum face area (-1 = no limit)
    
    # Twist and determinant
    "minTwist": 0.02,               # Minimum face twist
    "minDeterminant": 0.001,        # Minimum determinant
    "minFaceWeight": 0.02,          # Minimum face weight
    "minVolRatio": 0.01,            # Minimum volume ratio
    "minTriangleTwist": -1,         # Minimum triangle twist
    
    # Smoothing parameters
    "nSmoothScale": 4,              # Number of smoothing scale iterations
    "errorReduction": 0.75,         # Error reduction factor
    
    # Relaxed quality criteria (for difficult meshes)
    "relaxed": {
        "maxNonOrtho": 75,
        "maxBoundarySkewness": 30,
        "maxInternalSkewness": 8,
        "maxConcave": 85,
        "minFlatness": 0.3,
        "minVol": 1e-12,
        "minTetQuality": 1e-25,
        "minArea": -1,
        "minTwist": 0.01,
        "minDeterminant": 0.0001,
        "minFaceWeight": 0.01,
        "minVolRatio": 0.005,
        "minTriangleTwist": -1
    }
}

# --- Advanced Options ---
# `MERGED_PATCHES`: List of patches to be merged.
# Used for creating periodic boundaries or connecting patches
MERGED_PATCHES = []

# `WRITE_FLAGS`: Control what files are written during meshing.
WRITE_FLAGS = {
    "writeMesh": True,      # Write final mesh
    "writeSets": True,      # Write cell/face sets
    "writeZones": True      # Write cell/face zones
}

# --- Predefined Templates ---
# `TEMPLATE`: Select a predefined snappyHexMesh template
# Options: 'none', 'motorcycle', 'room', 'turbine', 'car', 'airfoil'
TEMPLATE = "none"

# `TEMPLATE_PARAMETERS`: Parameters for the selected template
TEMPLATE_PARAMETERS = {
    "motorcycle": {
        "geometry_file": "motorBike.obj",
        "feature_file": "motorBike.eMesh",
        "refinement_levels": (7, 7),
        "boundary_layers": False
    },
    "room": {
        "geometry_files": ["room.stl", "desk.stl", "door.stl"],
        "refinement_levels": (2, 3),
        "boundary_layers": False
    }
}

