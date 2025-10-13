# block_mesh_config.py

# =============================================================================
#           *** Enhanced User Input Configuration for blockMeshDict Generation ***
# =============================================================================
#
#   This enhanced configuration supports complex geometries with multiple blocks,
#   advanced grading, and sophisticated boundary conditions based on OpenFOAM
#   examples from Resources/Z Foam Collections.
#

# --- 1. Basic Geometry Definition ---

# `p0`: The minimum corner of the computational domain (x_min, y_min, z_min).
# This defines the bottom-left-front corner of the geometry.
# Example: (0.0, 0.0, 0.0) for a domain starting at the origin
p0 = (0.0, 0.0, 0.0)

# `p1`: The maximum corner of the computational domain (x_max, y_max, z_max).
# This defines the top-right-back corner of the geometry.
# Example: (0.5, 0.2, 0.1) for a channel 0.5m long, 0.2m wide, 0.1m high
p1 = (0.5, 0.2, 0.1)

# `scale`: Scaling factor for the mesh coordinates.
# Usually set to 1.0 for actual dimensions. Use other values to scale the entire geometry.
# Example: 1.0 for meters, 0.001 for millimeters, 1000 for kilometers
# Special scaling examples: 0.01 (cm to m), 0.0032 (mm to m), 1000 (m to km)
scale = 1.0

# --- 2. Mesh Complexity Level ---

# `mesh_type`: Type of mesh to generate
# Options: 'simple', 'multi_block', 'complex'
# - 'simple': Single block with uniform or simple grading
# - 'multi_block': Multiple blocks with different properties
# - 'complex': Advanced multi-block with edges, grading, and special features
mesh_type = "simple"

# --- 3. Simple Mesh Configuration (when mesh_type = "simple") ---

# `cells`: Number of cells in each direction (nx, ny, nz).
# This determines the mesh resolution. Higher numbers = finer mesh = longer computation time.
# Example: (50, 20, 50) means 50 cells in x-direction, 20 in y-direction, 50 in z-direction
# Total cells = nx * ny * nz = 50 * 20 * 50 = 50,000 cells
cells = (50, 20, 50)

# `grading`: Cell size grading for each direction (simpleGrading).
# Controls how cell sizes change across the domain.
# Example: (1, 1, 1) for uniform cells, (2, 1, 0.5) for graded cells
# Grading > 1: cells get larger in that direction
# Grading < 1: cells get smaller in that direction
grading = (1, 1, 1)

# --- 4. Multi-Block Configuration (when mesh_type = "multi_block" or "complex") ---

# `blocks`: List of block definitions for multi-block meshes
# Each block is defined by:
# - vertices: List of 8 vertex indices (0-7 for a hex)
# - cells: Number of cells in each direction (nx, ny, nz)
# - grading: Grading specification
# - grading_type: 'simpleGrading' or 'edgeGrading'
blocks = [
    {
        "name": "block1",
        "vertices": [0, 1, 2, 3, 4, 5, 6, 7],  # Standard hex vertices
        "cells": (40, 40, 1),
        "grading": (1, 1, 1),
        "grading_type": "simpleGrading"
    }
]

# `vertices`: Custom vertex definitions for complex geometries
# List of (x, y, z) coordinates. Vertices are referenced by index (0-based)
# Example: [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), ...]
vertices = []

# `edges`: Edge definitions for curved boundaries
# List of edge dictionaries with type and parameters
# Example: [{"type": "arc", "points": [0, 1], "centre": [0.5, 0.5, 0]}]
edges = []

# --- 5. Boundary Patch Names ---

# `patch_names`: Dictionary mapping geometric faces to boundary patch names.
# These names will be used in boundary condition files and OpenFOAM dictionaries.
# 
# Face identifiers:
#   'minX': Face at minimum X (x = p0[0])
#   'maxX': Face at maximum X (x = p1[0])
#   'minY': Face at minimum Y (y = p0[1])
#   'maxY': Face at maximum Y (y = p1[1])
#   'minZ': Face at minimum Z (z = p0[2])
#   'maxZ': Face at maximum Z (z = p1[2])
#
# Common patch types in OpenFOAM:
#   - 'patch': General boundary patch
#   - 'wall': Solid wall boundary
#   - 'symmetryPlane': Symmetry boundary
#   - 'empty': 2D simulation (front/back faces)
#   - 'cyclic': Periodic boundary condition
#   - 'wedge': Axisymmetric simulation
#
# Example for channel flow:
patch_names = {
    'minX': 'inlet',        # Inlet face (flow enters here)
    'maxX': 'outlet',       # Outlet face (flow exits here)
    'minY': 'frontWall',    # Front wall (solid boundary)
    'maxY': 'backWall',     # Back wall (solid boundary)
    'minZ': 'floor',        # Floor (solid boundary)
    'maxZ': 'ceiling'       # Ceiling (solid boundary)
}

# `custom_boundaries`: Custom boundary definitions for complex geometries
# List of boundary dictionaries with faces and properties
custom_boundaries = []

# --- 6. Advanced Meshing Options ---

# `merge_patch_pairs`: List of patch pairs to merge (for periodic boundaries).
# Example: [('leftWall', 'rightWall')] to create a periodic boundary
merge_patch_pairs = []

# `preserve_cell_zones`: Whether to preserve cell zones during mesh generation
preserve_cell_zones = False

# `preserve_face_zones`: Whether to preserve face zones during mesh generation
preserve_face_zones = False

# `preserve_point_zones`: Whether to preserve point zones during mesh generation
preserve_point_zones = False

# --- 7. Predefined Geometry Templates ---

# `geometry_template`: Select a predefined geometry template
# Options: 'none', 'channel', 'pipe', 'cavity', 'backward_facing_step', 'airfoil'
# When 'none' is selected, use custom geometry defined above
geometry_template = "none"

# `template_parameters`: Parameters for the selected template
# These override the basic geometry parameters when a template is selected
template_parameters = {
    # Channel flow template
    "channel": {
        "length": 1.0,      # Channel length [m]
        "height": 0.1,      # Channel height [m] 
        "width": 0.02,      # Channel width [m] (2D: small, 3D: actual width)
        "inlet_length": 0.2, # Inlet development length [m]
        "outlet_length": 0.2 # Outlet development length [m]
    },
    # Pipe flow template
    "pipe": {
        "length": 2.0,      # Pipe length [m]
        "diameter": 0.1,    # Pipe diameter [m]
        "inlet_length": 0.5, # Inlet development length [m]
        "outlet_length": 0.5 # Outlet development length [m]
    },
    # Cavity flow template
    "cavity": {
        "length": 1.0,      # Cavity length [m]
        "height": 1.0,      # Cavity height [m]
        "depth": 0.01,      # Cavity depth [m] (2D: small, 3D: actual depth)
        "lid_velocity": 1.0 # Lid velocity [m/s]
    }
}

# --- 8. Validation Settings ---

# `min_cell_size`: Minimum allowed cell size (for validation).
# Used to prevent extremely small cells that could cause numerical issues.
min_cell_size = 1e-6

# `max_cell_size`: Maximum allowed cell size (for validation).
# Used to prevent extremely large cells that could cause accuracy issues.
max_cell_size = 1.0

# `max_total_cells`: Maximum allowed total number of cells (for validation).
# Used to prevent creating meshes that are too large for available computational resources.
max_total_cells = 1000000

# `aspect_ratio_limit`: Maximum allowed cell aspect ratio
aspect_ratio_limit = 100.0

# `skewness_limit`: Maximum allowed cell skewness
skewness_limit = 0.8