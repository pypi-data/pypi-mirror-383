# u_field_writer.py

"""
Velocity Field Writer for OpenFOAM cases.

This writer handles the creation of velocity field (U) files in the 0 directory
with support for various boundary conditions and flow configurations.
"""

from ..foam_writer import FoamWriter


class UFieldWriter(FoamWriter):
    """
    A class to write an OpenFOAM velocity field (U) file.
    
    This writer supports various boundary conditions including fixedValue,
    noSlip, slip, inletOutlet, and other velocity-specific conditions.
    """

    def __init__(self, file_path, internal_velocity, boundary_conditions,
                 velocity_dimensions=[0, 1, -1, 0, 0, 0, 0]):
        """
        Initialize the UFieldWriter.

        Args:
            file_path (str): The full path to the output file '0/U'.
            internal_velocity (tuple): Internal field velocity vector (Ux, Uy, Uz).
            boundary_conditions (dict): Boundary conditions for each patch.
            velocity_dimensions (list): Velocity field dimensions.
        """
        super().__init__(file_path, foam_class="volVectorField", foam_object="U")
        self.internal_velocity = internal_velocity
        self.boundary_conditions = boundary_conditions
        self.velocity_dimensions = velocity_dimensions

    def _write_dimensions(self):
        """Write the dimensions section."""
        dims_str = ' '.join(map(str, self.velocity_dimensions))
        self.file_handle.write(f"dimensions      [{dims_str}];\n\n")

    def _write_internal_field(self):
        """Write the internal field section."""
        vel_str = ' '.join(map(str, self.internal_velocity))
        self.file_handle.write(f"internalField   uniform ({vel_str});\n\n")

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
            
            if 'inletValue' in bc:
                if isinstance(bc['inletValue'], (list, tuple)):
                    val_str = ' '.join(map(str, bc['inletValue']))
                    self.file_handle.write(f"        inletValue      uniform ({val_str});\n")
                else:
                    self.file_handle.write(f"        inletValue      uniform {bc['inletValue']};\n")
            
            self.file_handle.write("    }\n")
        
        self.file_handle.write("}\n\n")

    def _write_properties(self):
        """Write the main content of the velocity field file."""
        self._write_dimensions()
        self._write_internal_field()
        self._write_boundary_field()

    def write(self):
        """
        Writes the complete velocity field file.
        """
        print(f"Writing velocity field (U) to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
