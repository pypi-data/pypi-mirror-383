# lambda_field_writer.py

"""
Lambda Field Writer for OpenFOAM cases.

This writer handles the creation of lambda field (λ) files in the 0 directory
with support for level set functions, phase fields, and scalar transport.
"""

from ..foam_writer import FoamWriter


class LambdaFieldWriter(FoamWriter):
    """
    A class to write an OpenFOAM lambda field (λ) file.
    
    This writer supports various scalar field configurations including
    level set functions, phase fields, and general scalar transport.
    """

    def __init__(self, file_path, internal_lambda, boundary_conditions,
                 lambda_dimensions=[0, 0, 0, 0, 0, 0, 0]):
        """
        Initialize the LambdaFieldWriter.

        Args:
            file_path (str): The full path to the output file '0/lambda'.
            internal_lambda (float): Internal field lambda value.
            boundary_conditions (dict): Boundary conditions for each patch.
            lambda_dimensions (list): Lambda field dimensions.
        """
        super().__init__(file_path, foam_class="volScalarField", foam_object="lambda")
        self.internal_lambda = internal_lambda
        self.boundary_conditions = boundary_conditions
        self.lambda_dimensions = lambda_dimensions

    def _write_dimensions(self):
        """Write the dimensions section."""
        dims_str = ' '.join(map(str, self.lambda_dimensions))
        self.file_handle.write(f"dimensions      [{dims_str}];\n\n")

    def _write_internal_field(self):
        """Write the internal field section."""
        self.file_handle.write(f"internalField   uniform {self.internal_lambda};\n\n")

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
        """Write the main content of the lambda field file."""
        self._write_dimensions()
        self._write_internal_field()
        self._write_boundary_field()

    def write(self):
        """
        Writes the complete lambda field file.
        """
        print(f"Writing lambda field (λ) to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
