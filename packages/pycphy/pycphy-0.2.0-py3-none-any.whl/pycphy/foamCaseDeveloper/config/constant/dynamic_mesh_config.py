# config_dynamic_mesh.py

# =============================================================================
#           *** User Input for dynamicMeshDict ***
# =============================================================================

# --- Master Control ---
# Set this to True to include a dynamicMeshDict in the case setup,
# or False to skip it for a static mesh simulation.
WRITE_DYNAMIC_MESH_DICT = True

# --- Mesh Type Selection ---
# Choose the type of dynamic mesh behavior you want to configure.
# The selected dictionary below will be written to the file.
# Options:
#   "solidBodyMotion": For rigid body motion of a mesh zone (e.g., rotating fan).
#   "multiBodyOverset": For overset meshes with multiple moving bodies.
#   "adaptiveRefinement": For Adaptive Mesh Refinement (AMR) based on a field.
#   "morphingMesh": For deforming mesh using splines (e.g., shape optimization).
MESH_TYPE = "solidBodyMotion"


# =============================================================================
#           *** Pre-configured Mesh Property Dictionaries ***
# =============================================================================

# --- 1. Solid Body Motion ---
# Use this for cases where a part of the mesh moves as a rigid body without deforming,
# such as a propeller, fan, or stirrer.
SOLID_BODY_MOTION_PROPS = {
    # `dynamicFvMesh`: The top-level dynamic mesh class.
    #   Options:
    #     'dynamicMotionSolverFvMesh': The standard choice for mesh motion or deformation
    #                                  driven by a specified motion solver.
    "dynamicFvMesh": "dynamicMotionSolverFvMesh",

    # `solver`: The specific type of motion solver.
    #   Options:
    #     'solidBody': Moves a specified cellZone as a rigid body. Mesh does not deform.
    #     'displacementLaplacian': A common choice for deforming meshes where boundary
    #                              motion is propagated through the mesh by solving a
    #                              Laplacian equation for diffusivity.
    #     'velocityComponentLaplacian': Similar, but solves for velocity instead of displacement.
    "solver": "solidBody",

    # `solidBodyCoeffs`: A sub-dictionary containing settings for the `solidBody` solver.
    "solidBodyCoeffs": {
        # `cellZone`: The name of the cell zone in the mesh that will move.
        # This zone must be defined during meshing (e.g., in blockMeshDict or snappyHexMesh).
        "cellZone": "rotatingZone",

        # `solidBodyMotionFunction`: The type of rigid motion to apply.
        #   Options:
        #     'rotatingMotion': Pure rotation around an axis.
        #     'linearMotion': Constant velocity translation.
        #     'oscillatingLinearMotion': Sinusoidal back-and-forth linear movement.
        #     'oscillatingRotatingMotion': Sinusoidal rocking/pitching motion.
        #     'tabulated6DoFMotion': Reads 6-DoF motion (translation/rotation) from an
        #                            external text file. Very powerful for complex prescribed motions.
        #     'multiMotion': Allows for combining multiple motion functions.
        "solidBodyMotionFunction": "rotatingMotion",

        # `rotatingMotionCoeffs`: Sub-dictionary for the chosen motion function.
        # Each motion function has its own `...Coeffs` dictionary.
        "rotatingMotionCoeffs": {
            # `origin`: The center of rotation as a vector (x y z).
            "origin": (0, 0, 0),
            # `axis`: The axis of rotation as a vector (x y z). Does not need to be a unit vector.
            "axis": (0, 0, 1),
            # `omega`: The rotational speed in radians per second. Can be a number, or a Foam::DataEntry.
            "omega": 10.5
        }
    }
}

# --- 2. Multi-Body Overset Motion ---
# Use this for overset (or Chimera) meshes where multiple independent bodies
# move through a background mesh.
MULTI_BODY_OVERSET_PROPS = {
    # `dynamicFvMesh`: The required class for overset functionality.
    #   Options:
    #     'dynamicOversetFvMesh': For cases where the overset components move.
    #     'staticOversetFvMesh': For cases where overset zones are stationary,
    #                            but mesh connectivity still needs to be computed.
    "dynamicFvMesh": "dynamicOversetFvMesh",

    # `solver`: The motion solver.
    #   Options:
    #     'multiSolidBodyMotionSolver': Handles the motion of one or more named bodies,
    #                                   each with its own motion function. Ideal for complex scenes.
    #     'solidBody': Can be used if only a single overset zone is moving.
    #     'displacementLaplacian': Can be used to deform the overset mesh component.
    "solver": "multiSolidBodyMotionSolver",

    # `multiSolidBodyMotionSolverCoeffs`: Sub-dictionary defining each moving body.
    "multiSolidBodyMotionSolverCoeffs": {
        # Each entry in this dictionary is a separate moving body. The key name
        # ('movingZone1', 'propeller', etc.) must match a cellZone in the mesh.
        "movingZone1": {
            # `solidBodyMotionFunction`: See the list of functions in the SOLID_BODY_MOTION section.
            "solidBodyMotionFunction": "oscillatingLinearMotion",
            "oscillatingLinearMotionCoeffs": {
                "amplitude": (0.035, 0, 0),
                "omega": 2.094
            }
        },
        "movingZone2": {
            "solidBodyMotionFunction": "rotatingMotion",
            "rotatingMotionCoeffs": {
                "origin": (0.1, 0, 0),
                "axis": (0, 0, 1),
                "omega": -50.0
            }
        }
    }
}

# --- 3. Adaptive Mesh Refinement (AMR) ---
# Use this to automatically refine and unrefine the mesh in specific regions
# during the simulation, based on a scalar field.
ADAPTIVE_REFINEMENT_PROPS = {
    # `dynamicFvMesh`: The required class for AMR.
    "dynamicFvMesh": "dynamicRefineFvMesh",

    # `refineInterval`: How often (in number of time steps) the refinement criteria are checked.
    #   A value of 1 checks every time step. Larger values are more efficient but less responsive.
    "refineInterval": 1,

    # `field`: The name of the volScalarField that will drive the refinement. This field
    #          must exist in your case.
    #   Examples: 'alpha.water' (for VOF free surface), 'p' (pressure), 'magU' (velocity magnitude),
    #             a custom field calculated with functionObjects.
    "field": "alpha.water",

    # `lowerRefineLevel`: If the field value in a cell is below this, the
    #                     cell and its neighbors will be considered for un-refinement (coarsening).
    "lowerRefineLevel": 0.001,

    # `upperRefineLevel`: If the field value in a cell is above this, the
    #                     cell will be flagged for refinement (splitting).
    "upperRefineLevel": 0.999,

    # `unrefineLevel`: A tolerance used during the un-refinement (coarsening) step.
    #                  Cells marked for coarsening will only be merged if the field value difference
    #                  between them is small. This prevents coarsening across sharp gradients.
    "unrefineLevel": 0.0001,

    # `nBufferLayers`: Number of extra cell layers to keep refined around the primary refinement zone.
    #                  This is crucial for stability, preventing refinement/unrefinement from
    #                  happening right at a sharp interface.
    "nBufferLayers": 2,

    # `maxRefinement`: The maximum number of times an initial grid cell can be split.
    #   Level 0 = no refinement. Level 1 = split once. Level 2 = split twice (1 cell -> 8 in 3D).
    "maxRefinement": 2,

    # `maxCells`: An approximate hard limit on the total number of cells to prevent
    #             runaway refinement from using all available memory.
    "maxCells": 200000,

    # `correctFluxes`: A list of surfaceScalarFields (fluxes) that need to be corrected
    #                  when cell faces are created or destroyed by AMR. This is critical
    #                  for conservation. The format is a list of lists.
    "correctFluxes": [("phi", "U"), ("phi_0", "none")]
}


# --- 4. Morphing Mesh (Volumetric B-Splines) ---
# Use for cases where the mesh deforms smoothly, often for shape optimization
# or simulating structural deformation.
MORPHING_MESH_PROPS = {
    # `solver`: The motion solver for mesh deformation.
    #   Options:
    #     'volumetricBSplinesMotionSolver': A powerful and smooth morphing tool based on a
    #                                       control-point lattice.
    #     'laplacianMotionSolver': A simpler morphing solver based on solving a Laplacian
    #                              equation for mesh displacement.
    "solver": "volumetricBSplinesMotionSolver",

    # `volumetricBSplinesMotionSolverCoeffs`: Sub-dictionary for the B-splines solver.
    "volumetricBSplinesMotionSolverCoeffs": {
        # Each entry is a named "control point volume" that controls a region of the mesh.
        "airfoil": {
            # `type`: The coordinate system for the control points.
            #   Options: 'cartesian', 'cylindrical'.
            "type": "cartesian",
            # `nCPsU/V/W`: Number of control points in each direction (U,V,W map to X,Y,Z for cartesian).
            "nCPsU": 6,
            "nCPsV": 4,
            "nCPsW": 3,
            # `degreeU/V/W`: The polynomial degree of the spline curves. Higher degrees are smoother.
            "degreeU": 3,
            "degreeV": 3,
            "degreeW": 2,
            # `controlPointsDefinition`: How the initial control point positions are defined.
            #   Options:
            #     'axisAligned': Automatically creates a grid of points within the bounds below.
            #     'fromFile': Reads control point coordinates from a file.
            "controlPointsDefinition": "axisAligned",
            # `lowerCpBounds`/`upperCpBounds`: The bounding box for the 'axisAligned' control points.
            "lowerCpBounds": (0.1, -0.25, -0.1),
            "upperCpBounds": (0.9, 0.25, 1.1),
            # `confine...`: Boolean flags to restrict movement of control points.
            "confineWMovement": "true",
            "confineBoundaryControlPoints": "true",
        }
    }
}