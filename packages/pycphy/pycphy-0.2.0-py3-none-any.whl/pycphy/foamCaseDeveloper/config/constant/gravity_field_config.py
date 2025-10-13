# gravity_field_config.py

"""
Gravity Field Configuration for OpenFOAM cases.

This module provides configuration options for the gravity field (g) including
standard gravitational acceleration, custom gravity vectors, and variable
gravity fields for specialized simulations.
"""

# =============================================================================
#           *** User Input for gravity field (g) ***
# =============================================================================

# --- Master Control ---
# Set to True to write 'constant/g'.
WRITE_GRAVITY_FIELD = True

# =============================================================================
#           *** Gravity Field Configuration ***
# =============================================================================

GRAVITY_FIELD = {
    # Gravity vector components [m/s^2]
    # Standard Earth gravity: (0 0 -9.81) for downward gravity in z-direction
    # Zero gravity: (0 0 0) for microgravity or space simulations
    # Custom gravity: (gx gy gz) for arbitrary gravity directions
    "value": (0, 0, -9.81),  # Standard Earth gravity downward
    
    # Dimensions of the gravity field
    # [0 1 -2 0 0 0 0] = [length time^-2] = acceleration
    "dimensions": [0, 1, -2, 0, 0, 0, 0],
    
    # Description of the gravity configuration
    "description": "Standard Earth gravity (9.81 m/s^2 downward)",
}

# =============================================================================
#           *** Predefined Gravity Configurations ***
# =============================================================================
# Common gravity configurations for different simulation types

PREDEFINED_GRAVITY_CONFIGS = {
    "earth_standard": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Standard Earth gravity (9.81 m/s^2 downward)"
    },
    
    "earth_horizontal": {
        "value": (-9.81, 0, 0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Earth gravity in negative x-direction"
    },
    
    "earth_45_degree": {
        "value": (0, -6.93, -6.93),  # 9.81 * sin(45°), 9.81 * cos(45°)
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Earth gravity at 45° angle"
    },
    
    "moon": {
        "value": (0, 0, -1.62),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Moon gravity (1.62 m/s^2 downward)"
    },
    
    "mars": {
        "value": (0, 0, -3.71),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Mars gravity (3.71 m/s^2 downward)"
    },
    
    "jupiter": {
        "value": (0, 0, -24.79),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Jupiter gravity (24.79 m/s^2 downward)"
    },
    
    "microgravity": {
        "value": (0, 0, 0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Microgravity/zero gravity environment"
    },
    
    "centrifuge_100g": {
        "value": (0, 0, -981.0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Centrifuge at 100g (981 m/s^2 downward)"
    },
    
    "centrifuge_1000g": {
        "value": (0, 0, -9810.0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Centrifuge at 1000g (9810 m/s^2 downward)"
    },
    
    "rotating_frame": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity in rotating frame of reference"
    },
    
    "inclined_plane_30deg": {
        "value": (0, -4.905, -8.496),  # 9.81 * sin(30°), 9.81 * cos(30°)
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity on 30° inclined plane"
    },
    
    "inclined_plane_45deg": {
        "value": (0, -6.93, -6.93),  # 9.81 * sin(45°), 9.81 * cos(45°)
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity on 45° inclined plane"
    },
    
    "inclined_plane_60deg": {
        "value": (0, -8.496, -4.905),  # 9.81 * sin(60°), 9.81 * cos(60°)
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity on 60° inclined plane"
    },
    
    "custom_2d": {
        "value": (0, -9.81, 0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "2D gravity in y-direction"
    },
    
    "custom_3d": {
        "value": (-5.0, -5.0, -5.0),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Custom 3D gravity vector"
    },
    
    "buoyancy_test": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for buoyancy-driven flow tests"
    },
    
    "free_surface": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for free surface flow simulations"
    },
    
    "droplet_impact": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for droplet impact simulations"
    },
    
    "particle_sedimentation": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for particle sedimentation studies"
    },
    
    "convection_benchmark": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for natural convection benchmarks"
    },
    
    "turbulence_gravity": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for gravity-driven turbulence"
    },
    
    "stratified_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for stratified flow simulations"
    },
    
    "dam_break": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for dam break simulations"
    },
    
    "sloshing": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for tank sloshing simulations"
    },
    
    "wave_generation": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for wave generation and propagation"
    },
    
    "tsunami": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for tsunami simulation"
    },
    
    "flood_simulation": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for flood simulation"
    },
    
    "environmental_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for environmental flow studies"
    },
    
    "biomedical_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for biomedical flow simulations"
    },
    
    "food_processing": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for food processing simulations"
    },
    
    "mixing_tank": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for mixing tank simulations"
    },
    
    "chemical_reactor": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for chemical reactor simulations"
    },
    
    "heat_exchanger": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for heat exchanger simulations"
    },
    
    "boiler": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for boiler simulations"
    },
    
    "condenser": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for condenser simulations"
    },
    
    "evaporator": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for evaporator simulations"
    },
    
    "distillation_column": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for distillation column simulations"
    },
    
    "extraction_column": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for extraction column simulations"
    },
    
    "absorption_column": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for absorption column simulations"
    },
    
    "packed_bed": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for packed bed reactor simulations"
    },
    
    "fluidized_bed": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for fluidized bed simulations"
    },
    
    "bubble_column": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for bubble column simulations"
    },
    
    "stirred_tank": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for stirred tank simulations"
    },
    
    "pipeline_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for pipeline flow simulations"
    },
    
    "valve_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for valve flow simulations"
    },
    
    "pump_flow": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for pump flow simulations"
    },
    
    "compressor": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for compressor simulations"
    },
    
    "turbine": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for turbine simulations"
    },
    
    "wind_turbine": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for wind turbine simulations"
    },
    
    "hydro_turbine": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for hydro turbine simulations"
    },
    
    "solar_collector": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for solar collector simulations"
    },
    
    "geothermal": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for geothermal simulations"
    },
    
    "nuclear_reactor": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for nuclear reactor simulations"
    },
    
    "fusion_reactor": {
        "value": (0, 0, -9.81),
        "dimensions": [0, 1, -2, 0, 0, 0, 0],
        "description": "Gravity for fusion reactor simulations"
    },
}

# =============================================================================
#           *** Configuration Selection ***
# =============================================================================
# Select which predefined gravity configuration to use (overrides manual settings above)

USE_PREDEFINED_GRAVITY = None  # Set to gravity config name from PREDEFINED_GRAVITY_CONFIGS or None for manual config

# Example usage:
# USE_PREDEFINED_GRAVITY = "earth_standard"  # Will use standard Earth gravity
# USE_PREDEFINED_GRAVITY = "microgravity"    # Will use zero gravity
# USE_PREDEFINED_GRAVITY = "moon"            # Will use Moon gravity
