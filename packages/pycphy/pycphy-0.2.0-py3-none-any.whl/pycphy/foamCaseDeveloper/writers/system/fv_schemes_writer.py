# fv_schemes_writer.py

"""
Finite Volume Schemes Writer for OpenFOAM cases.

This writer handles the creation of fvSchemes files with support for various
discretization schemes for time derivatives, gradients, divergence, Laplacian,
interpolation, and surface normal gradients.
"""

from ..foam_writer import FoamWriter


class FvSchemesWriter(FoamWriter):
    """
    A class to write an OpenFOAM fvSchemes file.
    
    This writer supports comprehensive finite volume discretization schemes
    for various simulation types including laminar, turbulent, and multiphase flows.
    """

    def __init__(self, file_path, ddt_schemes, grad_schemes, div_schemes, 
                 laplacian_schemes, interpolation_schemes, sn_grad_schemes,
                 flux_required=None):
        """
        Initialize the FvSchemesWriter.

        Args:
            file_path (str): The full path to the output file 'fvSchemes'.
            ddt_schemes (dict): Time derivative schemes configuration.
            grad_schemes (dict): Gradient schemes configuration.
            div_schemes (dict): Divergence schemes configuration.
            laplacian_schemes (dict): Laplacian schemes configuration.
            interpolation_schemes (dict): Interpolation schemes configuration.
            sn_grad_schemes (dict): Surface normal gradient schemes configuration.
            flux_required (dict, optional): Flux required schemes configuration.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="fvSchemes")
        self.ddt_schemes = ddt_schemes
        self.grad_schemes = grad_schemes
        self.div_schemes = div_schemes
        self.laplacian_schemes = laplacian_schemes
        self.interpolation_schemes = interpolation_schemes
        self.sn_grad_schemes = sn_grad_schemes
        self.flux_required = flux_required or {}
    
    def validate_schemes(self):
        """
        Validate the schemes configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid = True
        
        # Validate ddt schemes
        valid_ddt = ['Euler', 'backward', 'CrankNicolson', 'localEuler', 
                    'steadyState', 'localSteadyState']
        if self.ddt_schemes.get('default') not in valid_ddt:
            print(f"Warning: Invalid ddt scheme '{self.ddt_schemes.get('default')}'")
            valid = False
        
        # Validate grad schemes
        valid_grad = ['Gauss linear', 'Gauss linearUpwind', 'Gauss linearUpwind grad',
                     'Gauss pointCellsLeastSquares', 'Gauss cellMDLimited', 
                     'Gauss faceMDLimited', 'leastSquares']
        if self.grad_schemes.get('default') not in valid_grad:
            print(f"Warning: Invalid grad scheme '{self.grad_schemes.get('default')}'")
            valid = False
        
        # Validate laplacian schemes
        valid_laplacian = ['Gauss linear', 'Gauss linear corrected', 'Gauss linear limited',
                          'Gauss linear limited corrected', 'Gauss linear uncorrected',
                          'Gauss linear orthogonal']
        if self.laplacian_schemes.get('default') not in valid_laplacian:
            print(f"Warning: Invalid laplacian scheme '{self.laplacian_schemes.get('default')}'")
            valid = False
        
        # Validate interpolation schemes
        valid_interpolation = ['linear', 'linearUpwind', 'skewCorrected linear', 'cubic',
                              'upwind', 'midPoint', 'harmonic', 'pointCellsLeastSquares']
        if self.interpolation_schemes.get('default') not in valid_interpolation:
            print(f"Warning: Invalid interpolation scheme '{self.interpolation_schemes.get('default')}'")
            valid = False
        
        # Validate snGrad schemes
        valid_sn_grad = ['corrected', 'uncorrected', 'limited', 'orthogonal', 'limited corrected']
        if self.sn_grad_schemes.get('default') not in valid_sn_grad:
            print(f"Warning: Invalid snGrad scheme '{self.sn_grad_schemes.get('default')}'")
            valid = False
        
        return valid
    
    def _write_scheme_section(self, section_name, schemes_dict):
        """
        Write a scheme section (ddtSchemes, gradSchemes, etc.).

        Args:
            section_name (str): Name of the scheme section.
            schemes_dict (dict): Dictionary containing scheme configurations.
        """
        self.file_handle.write(f"{section_name}\n")
        self.file_handle.write("{\n")
        
        # Write default scheme
        default_scheme = schemes_dict.get('default', 'none')
        self.file_handle.write(f"    default         {default_scheme};\n")
        
        # Write field-specific schemes
        field_specific = schemes_dict.get('fieldSpecific', {})
        for field, scheme in field_specific.items():
            self.file_handle.write(f"    {field:<20} {scheme};\n")
        
        self.file_handle.write("}\n\n")

    def _write_flux_required(self):
        """Write fluxRequired section if enabled."""
        if not self.flux_required.get('enabled', False):
            return
            
        self.file_handle.write("fluxRequired\n")
        self.file_handle.write("{\n")
        
        fields = self.flux_required.get('fields', [])
        for field in fields:
            self.file_handle.write(f"    {field};\n")
        
        self.file_handle.write("}\n\n")

    def _write_properties(self):
        """Writes the main content of the fvSchemes file."""
        self._write_scheme_section("ddtSchemes", self.ddt_schemes)
        self._write_scheme_section("gradSchemes", self.grad_schemes)
        self._write_scheme_section("divSchemes", self.div_schemes)
        self._write_scheme_section("laplacianSchemes", self.laplacian_schemes)
        self._write_scheme_section("interpolationSchemes", self.interpolation_schemes)
        self._write_scheme_section("snGradSchemes", self.sn_grad_schemes)
        self._write_flux_required()

    def write(self):
        """
        Writes the complete fvSchemes file.
        """
        print(f"Writing fvSchemes to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
