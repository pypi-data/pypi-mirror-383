# decompose_par_writer.py

"""
Decompose Par Writer for OpenFOAM cases.

This writer handles the creation of decomposeParDict files with support for
various decomposition methods and load balancing strategies for parallel processing.
"""

from ..foam_writer import FoamWriter


class DecomposeParWriter(FoamWriter):
    """
    A class to write an OpenFOAM decomposeParDict file.
    
    This writer supports comprehensive decomposition configurations for various
    simulation types and parallel processing scenarios.
    """

    def __init__(self, file_path, number_of_subdomains, method, coeffs=None, 
                 options=None, fields=None, preserve_patches=None, 
                 preserve_cell_zones=None, preserve_face_zones=None, 
                 preserve_point_zones=None):
        """
        Initialize the DecomposeParWriter.

        Args:
            file_path (str): The full path to the output file 'decomposeParDict'.
            number_of_subdomains (int): Number of domains to decompose into.
            method (str): Decomposition method.
            coeffs (dict, optional): Decomposition coefficients.
            options (dict, optional): Additional decomposition options.
            fields (list, optional): Fields to decompose.
            preserve_patches (list, optional): Patches to preserve.
            preserve_cell_zones (list, optional): Cell zones to preserve.
            preserve_face_zones (list, optional): Face zones to preserve.
            preserve_point_zones (list, optional): Point zones to preserve.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="decomposeParDict")
        self.number_of_subdomains = number_of_subdomains
        self.method = method
        self.coeffs = coeffs or {}
        self.options = options or {}
        self.fields = fields or []
        self.preserve_patches = preserve_patches or []
        self.preserve_cell_zones = preserve_cell_zones or []
        self.preserve_face_zones = preserve_face_zones or []
        self.preserve_point_zones = preserve_point_zones or []
    
    def validate_decomposition(self):
        """
        Validate the decomposition configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid = True
        
        # Validate number of subdomains
        if not isinstance(self.number_of_subdomains, int) or self.number_of_subdomains < 1:
            print("Warning: numberOfSubdomains must be a positive integer")
            valid = False
        
        # Validate method
        valid_methods = [
            'simple', 'hierarchical', 'scotch', 'metis', 'manual',
            'multiLevel', 'structured', 'kahip', 'ptscotch'
        ]
        if self.method not in valid_methods:
            print(f"Warning: Invalid decomposition method '{self.method}'. Valid methods: {valid_methods}")
            valid = False
        
        # Validate coefficients based on method
        if self.method == 'simple' and 'simpleCoeffs' not in self.coeffs:
            print("Warning: Simple method requires simpleCoeffs")
            valid = False
        
        if self.method == 'scotch' and 'scotchCoeffs' not in self.coeffs:
            print("Warning: Scotch method requires scotchCoeffs")
            valid = False
        
        return valid
    
    def _write_dict_recursively(self, data_dict, indent_level):
        """
        Recursively writes a dictionary's contents, handling nested dictionaries.

        Args:
            data_dict (dict): The dictionary to write.
            indent_level (int): The current level of indentation.
        """
        indent = "    " * indent_level
        # Calculate padding for alignment within the current dictionary level
        max_key_len = max((len(k) for k in data_dict.keys()), default=0)

        for key, value in data_dict.items():
            if isinstance(value, dict):
                # If the value is another dictionary, start a new block
                self.file_handle.write(f"{indent}{key}\n")
                self.file_handle.write(f"{indent}{{\n")
                self._write_dict_recursively(value, indent_level + 1)
                self.file_handle.write(f"{indent}}}\n\n")
            elif isinstance(value, (list, tuple)):
                # Write lists and tuples
                if isinstance(value, list) and value and isinstance(value[0], str):
                    # Quote string items
                    val_str = ' '.join([f'"{v}"' for v in value])
                else:
                    # Standard numbers
                    val_str = ' '.join(map(str, value))
                
                self.file_handle.write(f"{indent}{key:<{max_key_len}} ({val_str});\n")
            elif isinstance(value, bool):
                # Write booleans as 'true' or 'false'
                val_str = "true" if value else "false"
                self.file_handle.write(f"{indent}{key:<{max_key_len}} {val_str};\n")
            else:
                # Otherwise, it's a simple key-value pair
                padded_key = f"{key:<{max_key_len}}"
                self.file_handle.write(f"{indent}{padded_key}    {value};\n")

    def _write_coeffs(self):
        """Write decomposition coefficients section."""
        if not self.coeffs:
            return
            
        # Write method-specific coefficients
        method_coeffs = self.coeffs.get(f"{self.method}Coeffs", {})
        if method_coeffs:
            self.file_handle.write(f"{self.method}Coeffs\n")
            self.file_handle.write("{\n")
            self._write_dict_recursively(method_coeffs, indent_level=1)
            self.file_handle.write("}\n\n")

    def _write_options(self):
        """Write decomposition options section."""
        if not self.options:
            return
            
        self.file_handle.write("options\n")
        self.file_handle.write("{\n")
        self._write_dict_recursively(self.options, indent_level=1)
        self.file_handle.write("}\n\n")

    def _write_fields(self):
        """Write fields section."""
        if not self.fields:
            return
            
        self.file_handle.write("fields\n")
        self.file_handle.write("(\n")
        
        for field in self.fields:
            self.file_handle.write(f'    "{field}"\n')
        
        self.file_handle.write(")\n\n")

    def _write_preserve_sections(self):
        """Write preserve sections."""
        # Write preserve patches
        if self.preserve_patches:
            self.file_handle.write("preservePatches\n")
            self.file_handle.write("(\n")
            for patch in self.preserve_patches:
                self.file_handle.write(f'    "{patch}"\n')
            self.file_handle.write(")\n\n")
        
        # Write preserve cell zones
        if self.preserve_cell_zones:
            self.file_handle.write("preserveCellZones\n")
            self.file_handle.write("(\n")
            for zone in self.preserve_cell_zones:
                self.file_handle.write(f'    "{zone}"\n')
            self.file_handle.write(")\n\n")
        
        # Write preserve face zones
        if self.preserve_face_zones:
            self.file_handle.write("preserveFaceZones\n")
            self.file_handle.write("(\n")
            for zone in self.preserve_face_zones:
                self.file_handle.write(f'    "{zone}"\n')
            self.file_handle.write(")\n\n")
        
        # Write preserve point zones
        if self.preserve_point_zones:
            self.file_handle.write("preservePointZones\n")
            self.file_handle.write("(\n")
            for zone in self.preserve_point_zones:
                self.file_handle.write(f'    "{zone}"\n')
            self.file_handle.write(")\n\n")

    def _write_properties(self):
        """Writes the main content of the decomposeParDict file."""
        # Write number of subdomains
        self.file_handle.write(f"numberOfSubdomains    {self.number_of_subdomains};\n\n")
        
        # Write method
        self.file_handle.write(f"method                 {self.method};\n\n")
        
        # Write coefficients
        self._write_coeffs()
        
        # Write options
        self._write_options()
        
        # Write fields
        self._write_fields()
        
        # Write preserve sections
        self._write_preserve_sections()

    def write(self):
        """
        Writes the complete decomposeParDict file.
        """
        print(f"Writing decomposeParDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
