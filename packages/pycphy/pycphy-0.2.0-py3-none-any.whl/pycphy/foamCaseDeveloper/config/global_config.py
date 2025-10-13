# global_config.py

# =============================================================================
#           *** Global Configuration for pycphy foamCaseDeveloper ***
# =============================================================================
#
#   This file contains global settings and case information that applies
#   to the entire OpenFOAM case setup process.
#

# --- Case Information ---

# `case_name`: The name of the OpenFOAM case directory to be created.
# This will be the main directory containing all case files.
case_name = "channelFlow"

# `case_description`: A brief description of the simulation case.
# This is used for documentation and logging purposes.
case_description = "Channel flow simulation with RAS turbulence model"

# `author_name`: Name of the person creating this case.
author_name = "Sanjeev Bashyal"

# `author_email`: Email contact for the case author.
author_email = "sanjeev.bashyal@example.com"

# `creation_date`: Date when the case was created (automatically set).
# Format: YYYY-MM-DD
creation_date = "2025-01-09"

# --- Output Configuration ---

# `output_directory`: The base directory where the case will be created.
# Use "." for current directory, or specify a full path.
output_directory = "."

# `overwrite_existing`: Whether to overwrite an existing case directory.
# Options: True (overwrite), False (create with suffix if exists)
overwrite_existing = True

# `create_backup`: Whether to create a backup of existing case before overwriting.
# Only applies when overwrite_existing = True
create_backup = False

# --- Logging and Verbosity ---

# `verbose_output`: Enable detailed output during case creation.
# Options: True (detailed), False (minimal)
verbose_output = True

# `log_to_file`: Whether to save case creation log to a file.
log_to_file = True

# `log_filename`: Name of the log file (if log_to_file = True).
log_filename = "case_creation.log"

# --- Validation Settings ---

# `validate_geometry`: Enable geometry validation before mesh generation.
# Checks for valid dimensions, positive cell counts, etc.
validate_geometry = True

# `validate_control`: Enable control parameter validation.
# Checks for valid solver names, time parameters, etc.
validate_control = True

# `validate_turbulence`: Enable turbulence model validation.
# Checks for valid model names and parameters.
validate_turbulence = True

# --- Advanced Options ---

# `auto_create_directories`: Automatically create necessary directories.
# Options: True (auto-create), False (fail if directories don't exist)
auto_create_directories = True

# `cleanup_on_failure`: Remove partially created case files if setup fails.
# Options: True (cleanup), False (keep partial files for debugging)
cleanup_on_failure = True

# `parallel_processing`: Enable parallel processing for large cases.
# Currently not implemented, reserved for future use.
parallel_processing = False
