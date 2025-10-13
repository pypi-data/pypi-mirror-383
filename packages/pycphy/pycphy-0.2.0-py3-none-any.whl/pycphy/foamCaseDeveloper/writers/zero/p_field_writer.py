# p_field_writer.py

"""
Pressure Field Writer for OpenFOAM cases.

This writer handles the creation of pressure field (p) files in the 0 directory
with support for various boundary conditions and field configurations.
"""

from ..foam_writer import FoamWriter


class PFieldWriter(FoamWriter):
    """
    A class to write an OpenFOAM pressure field (p) file.
    
    This writer supports various boundary conditions including fixedValue,
    zeroGradient, and other pressure-specific conditions.
    """

    def __init__(self, file_path, internal_pressure, boundary_conditions, 
                 ref_pressure_cell=0, ref_pressure_value=0.0, 
                 pressure_dimensions=[0, 2, -2, 0, 0, 0, 0]):
        """
        Initialize the PFieldWriter.

        Args:
            file_path (str): The full path to the output file '0/p'.
            internal_pressure (float): Internal field pressure value.
            boundary_conditions (dict): Boundary conditions for each patch.
            ref_pressure_cell (int): Reference pressure cell for pressure correction.
            ref_pressure_value (float): Reference pressure value.
            pressure_dimensions (list): Pressure field dimensions.
        """
        super().__init__(file_path, foam_class="volScalarField", foam_object="p")
        self.internal_pressure = internal_pressure
        self.boundary_conditions = boundary_conditions
        self.ref_pressure_cell = ref_pressure_cell
        self.ref_pressure_value = ref_pressure_value
        self.pressure_dimensions = pressure_dimensions

    def _write_dimensions(self):
        """Write the dimensions section."""
        dims_str = ' '.join(map(str, self.pressure_dimensions))
        self.file_handle.write(f"dimensions      [{dims_str}];\n\n")

    def _write_internal_field(self):
        """Write the internal field section."""
        self.file_handle.write(f"internalField   uniform {self.internal_pressure};\n\n")

    def _write_boundary_field(self):
        """Write the boundary field section."""
        self.file_handle.write("boundaryField\n")
        self.file_handle.write("{\n")
        
        for patch_name, bc in self.boundary_conditions.items():
            self.file_handle.write(f"    {patch_name}\n")
            self.file_handle.write("    {\n")
            self.file_handle.write(f"        type            {bc['type']};\n")
            
            if 'value' in bc:
                self.file_handle.write(f"        value           uniform {bc['value']};\n")
            
            self.file_handle.write("    }\n")
        
        self.file_handle.write("}\n\n")

    def _write_properties(self):
        """Write the main content of the pressure field file."""
        self._write_dimensions()
        self._write_internal_field()
        self._write_boundary_field()

    def write(self):
        """
        Writes the complete pressure field file.
        """
        print(f"Writing pressure field (p) to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
