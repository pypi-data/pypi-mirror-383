# gravity_field_writer.py

"""
Gravity Field Writer for OpenFOAM cases.

This writer handles the creation of gravity field (g) files with support for
various gravity configurations including standard Earth gravity, custom gravity
vectors, and specialized gravity fields for different simulation types.
"""

from ..foam_writer import FoamWriter


class GravityFieldWriter(FoamWriter):
    """
    A class to write an OpenFOAM gravity field (g) file.
    
    This writer supports various gravity configurations including standard
    gravitational acceleration, custom gravity vectors, and specialized
    gravity fields for different simulation types.
    """

    def __init__(self, file_path, gravity_value, dimensions=None):
        """
        Initialize the GravityFieldWriter.

        Args:
            file_path (str): The full path to the output file 'g'.
            gravity_value (tuple): Gravity vector (gx, gy, gz) [m/s^2].
            dimensions (list, optional): Dimensions of the gravity field.
        """
        super().__init__(file_path, foam_class="uniformDimensionedVectorField", foam_object="g")
        self.gravity_value = gravity_value
        self.dimensions = dimensions or [0, 1, -2, 0, 0, 0, 0]  # Default: acceleration dimensions
    
    def validate_gravity_field(self):
        """
        Validate the gravity field configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid = True
        
        # Check if gravity_value is a tuple/list with 3 components
        if not isinstance(self.gravity_value, (tuple, list)) or len(self.gravity_value) != 3:
            print("Warning: Gravity value must be a tuple/list with 3 components (gx, gy, gz)")
            valid = False
        
        # Check if all components are numeric
        for i, component in enumerate(self.gravity_value):
            if not isinstance(component, (int, float)):
                print(f"Warning: Gravity component {i} must be numeric")
                valid = False
        
        # Check dimensions
        if not isinstance(self.dimensions, (tuple, list)) or len(self.dimensions) != 7:
            print("Warning: Dimensions must be a tuple/list with 7 components")
            valid = False
        
        return valid
    
    def _write_properties(self):
        """Writes the main content of the gravity field file."""
        # Write dimensions
        dimensions_str = ' '.join(map(str, self.dimensions))
        self.file_handle.write(f"dimensions      [{dimensions_str}];\n")
        
        # Write gravity vector
        gravity_str = ' '.join(map(str, self.gravity_value))
        self.file_handle.write(f"value           ({gravity_str});\n")

    def write(self):
        """
        Writes the complete gravity field file.
        """
        print(f"Writing gravity field (g) to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
