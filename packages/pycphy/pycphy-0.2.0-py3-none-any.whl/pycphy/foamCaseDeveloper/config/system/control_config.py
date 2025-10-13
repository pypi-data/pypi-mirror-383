# control_config.py

# =============================================================================
#           *** User Input for controlDict Parameters ***
# =============================================================================
#
#   This file defines the simulation control settings that will be written
#   to the controlDict file. Modify the values in the `control_params`
#   dictionary below.
#

control_params = {
    # --- Solver and Time Control ---

    # `application`: The name of the OpenFOAM solver to be used.
    # This determines which physics equations will be solved.
    # Common Options:
    #   'icoFoam': Incompressible, laminar flow solver
    #   'simpleFoam': Steady-state, incompressible, turbulent flow solver
    #   'pimpleFoam': Transient, incompressible, turbulent flow solver
    #   'interFoam': Two-phase flow solver (VOF method)
    #   'rhoSimpleFoam': Steady-state, compressible flow solver
    #   'rhoPimpleFoam': Transient, compressible flow solver
    #   'buoyantFoam': Natural convection solver
    "application": "interFoam",

    # `startFrom`: Controls how the simulation starts.
    # This determines the initial time and data source for the simulation.
    # Options:
    #   'startTime': Starts from the time specified in 'startTime'. (Most common)
    #   'firstTime': Starts from the earliest time-step directory found in the case.
    #   'latestTime': Starts from the latest time-step directory. (For restarting)
    "startFrom": "startTime",

    # `startTime`: The simulation time to start from. Usually 0 for a new run.
    # This is the initial time value for the simulation.
    # Example: 0.0 for starting from t=0, 1.5 for restarting from t=1.5
    "startTime": 0,

    # `stopAt`: The condition that will end the simulation.
    # This determines when the solver will stop running.
    # Options:
    #   'endTime': Stops when the simulation time reaches 'endTime'. (Most common)
    #   'writeNow': Writes the current time step and then stops.
    #   'noWriteNow': Stops immediately without writing.
    #   'runTime': Stops after a specified wall-clock time (in seconds).
    "stopAt": "endTime",

    # `endTime`: The simulation time to stop at.
    # This is the final time value for the simulation.
    # Example: 1.0 for running until t=1.0 seconds
    "endTime": 1.0,

    # `deltaT`: The time step (Δt) for the simulation. This is a critical
    # parameter for numerical stability and accuracy.
    # Smaller values = more stable but slower computation.
    # Larger values = faster but potentially unstable.
    # Typical range: 1e-6 to 1e-2 depending on the problem
    "deltaT": 0.001,

    # --- Data Output (Write) Control ---

    # `writeControl`: Determines how often results are written to disk.
    # This controls the frequency of data output during the simulation.
    # Options:
    #   'adjustableRunTime': Writes at intervals of simulation time specified by
    #                        'writeInterval', adjusting to match a multiple of deltaT. (Recommended)
    #   'runTime': Writes at intervals of simulation time, may not align with deltaT.
    #   'timeStep': Writes every N time steps, where N is 'writeInterval'.
    #   'cpuTime': Writes at intervals of CPU time (wall-clock seconds).
    "writeControl": "adjustableRunTime",

    # `writeInterval`: The frequency of writing data. Its meaning depends on 'writeControl'.
    # For 'adjustableRunTime' or 'runTime': seconds of simulation time
    # For 'timeStep': integer number of steps
    # For 'cpuTime': wall-clock seconds
    # Example: 0.05 means write every 0.05 seconds of simulation time
    "writeInterval": 0.05,

    # `purgeWrite`: Cleans up old time-step directories to save disk space.
    # This prevents the case directory from becoming too large.
    # Options:
    #   0: Keep all saved time steps (default, uses more disk space)
    #   N > 0: Keep only the latest N time-step directories
    # Example: 5 means keep only the latest 5 time directories
    "purgeWrite": 0,

    # `writeFormat`: The format for the output data files.
    # This affects file size and read/write speed.
    # Options:
    #   'ascii': Human-readable text format. Good for debugging, larger file sizes.
    #   'binary': Machine-readable binary format. Smaller files, faster I/O.
    "writeFormat": "ascii",

    # `writePrecision`: Number of significant figures for data in 'ascii' format.
    # Higher precision = larger files but more accurate output.
    # Typical range: 6-12 digits
    "writePrecision": 6,

    # `writeCompression`: Compresses the output files to save space.
    # This reduces disk usage but may slow down I/O slightly.
    # Options: 'on' (or 'compressed'), 'off' (or 'uncompressed')
    "writeCompression": "off",

    # `timeFormat`: The format used for the names of the time-step directories.
    # This affects how time directories are named and sorted.
    # Options: 'general', 'fixed', 'scientific'. 'general' is usually best.
    "timeFormat": "general",

    # `timePrecision`: Number of significant figures for the time-step directory names.
    # This affects the precision of time directory names.
    # Typical range: 6-12 digits
    "timePrecision": 6,

    # --- Run-Time Modification and Time-Step Adjustment ---

    # `runTimeModifiable`: Allows dictionaries (like this one) to be re-read
    # and updated while the simulation is running.
    # This is very useful for adjusting parameters during long simulations.
    # Options: 'yes' (or 'true'), 'no' (or 'false')
    "runTimeModifiable": "yes",

    # `adjustTimeStep`: Enables automatic time-step adjustment to meet criteria
    # like the Courant number (`maxCo`).
    # This is essential for many simulations to maintain stability.
    # Options: 'on' (or 'yes'), 'off' (or 'no')
    "adjustTimeStep": "on",

    # `maxCo`: The maximum allowable Courant number. If 'adjustTimeStep' is on,
    # the solver will reduce 'deltaT' to ensure the Courant number does not
    # exceed this value. A value of < 1 is required for many solvers.
    # Typical range: 0.1 to 1.0 (lower = more stable but slower)
    "maxCo": 1,
    
    # `maxAlphaCo`: Similar to `maxCo`, but specifically for the interface-capturing
    # part of multiphase solvers like 'interFoam'.
    # This controls the stability of the volume fraction equation.
    # Typical range: 0.1 to 1.0
    "maxAlphaCo": 1,

    # `maxDeltaT`: An absolute maximum limit for the time step, regardless of
    # the Courant number. Prevents the time step from becoming excessively large.
    # This is a safety measure to prevent numerical instability.
    # Example: 1.0 means time step will never exceed 1.0 seconds
    "maxDeltaT": 1,

    # --- Additional Solver-Specific Parameters ---

    # `nCorrectors`: Number of pressure correction iterations (for PIMPLE algorithm).
    # Used by pimpleFoam and similar solvers.
    # Typical range: 1-5 (higher = more accurate but slower)
    "nCorrectors": 2,

    # `nNonOrthogonalCorrectors`: Number of non-orthogonal correction iterations.
    # Used to improve accuracy on non-orthogonal meshes.
    # Typical range: 0-3 (higher = more accurate but slower)
    "nNonOrthogonalCorrectors": 0,

    # `pRefCell`: Reference pressure cell (for pressure field).
    # Used to set the reference pressure in the pressure field.
    # Example: 0 (uses cell 0 as reference)
    "pRefCell": 0,

    # `pRefValue`: Reference pressure value (for pressure field).
    # The pressure value at the reference cell.
    # Example: 0.0 (atmospheric pressure reference)
    "pRefValue": 0.0,

    # --- Library Dependencies ---
    
    # `libs`: List of additional libraries to load
    # These are required for certain solvers or function objects
    # Example: ["interfaceTrackingFvMesh"] for interFoam with interface tracking
    "libs": [],

    # --- Advanced Time Control ---
    
    # `maxAlphaCo`: Maximum allowable alpha Courant number for multiphase flows
    # Controls interface tracking stability in VOF simulations
    # Typical range: 0.1 to 1.0
    "maxAlphaCo": 1.0,

    # `maxDi`: Maximum allowable diffusion number
    # Used for stability control in diffusion-dominated problems
    "maxDi": 10.0,

    # `maxDeltaT`: Maximum time step limit (safety measure)
    # Prevents time step from becoming too large
    "maxDeltaT": 1.0,

    # --- Function Objects and Monitoring ---
    
    # `functions`: Dictionary of function objects for monitoring and data collection
    # These enable real-time monitoring, data sampling, and post-processing
    "functions": {
        # Example probes for monitoring specific locations
        "probes": {
            "type": "probes",
            "libs": ["sampling"],
            "fields": ["p", "U", "T"],
            "probeLocations": [
                (0.1, 0.05, 0.05),  # Near inlet
                (0.5, 0.05, 0.05),  # Mid domain
                (0.9, 0.05, 0.05)   # Near outlet
            ],
            "writeControl": "timeStep",
            "writeInterval": 10
        }
    },

    # --- Solver-Specific Advanced Options ---
    
    # `residualControl`: Convergence criteria for iterative solvers
    # Controls when the solver considers a time step converged
    "residualControl": {
        "p": 1e-6,
        "U": 1e-6,
        "k": 1e-6,
        "epsilon": 1e-6,
        "omega": 1e-6,
        "alpha.water": 1e-6
    },

    # `relaxationFactors`: Under-relaxation factors for field updates
    # Controls stability and convergence rate
    "relaxationFactors": {
        "fields": {
            "p": 0.3,
            "pFinal": 1.0
        },
        "equations": {
            "U": 0.7,
            "k": 0.7,
            "epsilon": 0.7,
            "omega": 0.7
        }
    },

    # `momentumPredictor`: Whether to use momentum predictor
    # Improves convergence for transient simulations
    "momentumPredictor": "yes",

    # `transonic`: Whether to use transonic corrections
    # For compressible flows near Mach 1
    "transonic": "no",

    # `consistent`: Whether to use consistent discretization
    # For better accuracy on non-orthogonal meshes
    "consistent": "yes",

    # --- Turbulence Model Settings ---
    
    # `turbulence`: Turbulence model configuration
    "turbulence": "on",
    
    # `printCoeffs`: Whether to print turbulence model coefficients
    "printCoeffs": "on",

    # --- Solution Control ---
    
    # `cacheAgglomeration`: Cache agglomeration for AMG solvers
    "cacheAgglomeration": "on",
    
    # `agglomerator`: Agglomeration method for AMG
    "agglomerator": "faceAreaPair",
    
    # `mergeLevels`: Number of levels to merge in AMG
    "mergeLevels": 1,

    # --- Monitoring and Output ---
    
    # `writeResiduals`: Whether to write residual information
    "writeResiduals": "yes",
    
    # `writeMesh`: Whether to write mesh information
    "writeMesh": "no",
    
    # `writeGraph`: Whether to write convergence graphs
    "writeGraph": "yes"
}