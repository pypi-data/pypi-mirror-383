# f_field_writer.py

"""
Force Field Writer for OpenFOAM cases.

This writer handles the creation of force field (f) files in the 0 directory
with support for various body force configurations.
"""

from ..foam_writer import FoamWriter


class FFieldWriter(FoamWriter):
    """
    A class to write an OpenFOAM force field (f) file.
    
    This writer supports various body forces including gravity, buoyancy,
    centrifugal, electromagnetic, and other force configurations.
    """

    def __init__(self, file_path, internal_force, boundary_conditions,
                 force_dimensions=[0, 1, -2, 0, 0, 0, 0]):
        """
        Initialize the FFieldWriter.

        Args:
            file_path (str): The full path to the output file '0/f'.
            internal_force (tuple): Internal field force vector (fx, fy, fz).
            boundary_conditions (dict): Boundary conditions for each patch.
            force_dimensions (list): Force field dimensions.
        """
        super().__init__(file_path, foam_class="volVectorField", foam_object="f")
        self.internal_force = internal_force
        self.boundary_conditions = boundary_conditions
        self.force_dimensions = force_dimensions

    def _write_dimensions(self):
        """Write the dimensions section."""
        dims_str = ' '.join(map(str, self.force_dimensions))
        self.file_handle.write(f"dimensions      [{dims_str}];\n\n")

    def _write_internal_field(self):
        """Write the internal field section."""
        force_str = ' '.join(map(str, self.internal_force))
        self.file_handle.write(f"internalField   uniform ({force_str});\n\n")

    def _write_boundary_field(self):
        """Write the boundary field section."""
        self.file_handle.write("boundaryField\n")
        self.file_handle.write("{\n")
        
        for patch_name, bc in self.boundary_conditions.items():
            self.file_handle.write(f"    {patch_name}\n")
            self.file_handle.write("    {\n")
            self.file_handle.write(f"        type            {bc['type']};\n")
            
            if 'value' in bc:
                if isinstance(bc['value'], (list, tuple)):
                    val_str = ' '.join(map(str, bc['value']))
                    self.file_handle.write(f"        value           uniform ({val_str});\n")
                else:
                    self.file_handle.write(f"        value           uniform {bc['value']};\n")
            
            self.file_handle.write("    }\n")
        
        self.file_handle.write("}\n\n")

    def _write_properties(self):
        """Write the main content of the force field file."""
        self._write_dimensions()
        self._write_internal_field()
        self._write_boundary_field()

    def write(self):
        """
        Writes the complete force field file.
        """
        print(f"Writing force field (f) to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
