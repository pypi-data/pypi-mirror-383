# fv_options_writer.py

"""
Finite Volume Options Writer for OpenFOAM cases.

This writer handles the creation of fvOptions files with support for various
source terms, constraints, and modifications including momentum, thermal,
species, turbulence, and pressure sources.
"""

from ..foam_writer import FoamWriter


class FvOptionsWriter(FoamWriter):
    """
    A class to write an OpenFOAM fvOptions file.
    
    This writer supports comprehensive finite volume source terms and constraints
    for various simulation types including momentum, thermal, species, and 
    multiphase flow simulations.
    """

    def __init__(self, file_path, momentum_sources=None, thermal_sources=None,
                 species_sources=None, turbulence_sources=None, pressure_sources=None,
                 volume_fraction_sources=None, advanced_sources=None):
        """
        Initialize the FvOptionsWriter.

        Args:
            file_path (str): The full path to the output file 'fvOptions'.
            momentum_sources (dict, optional): Momentum sources configuration.
            thermal_sources (dict, optional): Thermal sources configuration.
            species_sources (dict, optional): Species sources configuration.
            turbulence_sources (dict, optional): Turbulence sources configuration.
            pressure_sources (dict, optional): Pressure sources configuration.
            volume_fraction_sources (dict, optional): Volume fraction sources configuration.
            advanced_sources (dict, optional): Advanced sources configuration.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="fvOptions")
        self.momentum_sources = momentum_sources or {}
        self.thermal_sources = thermal_sources or {}
        self.species_sources = species_sources or {}
        self.turbulence_sources = turbulence_sources or {}
        self.pressure_sources = pressure_sources or {}
        self.volume_fraction_sources = volume_fraction_sources or {}
        self.advanced_sources = advanced_sources or {}
    
    def validate_sources(self):
        """
        Validate the sources configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid = True
        
        # Validate momentum sources
        if self.momentum_sources.get('enabled', False):
            sources = self.momentum_sources.get('sources', [])
            for source in sources:
                if 'type' not in source or 'fields' not in source:
                    print(f"Warning: Momentum source missing required fields: {source.get('name', 'unnamed')}")
                    valid = False
        
        # Validate thermal sources
        if self.thermal_sources.get('enabled', False):
            sources = self.thermal_sources.get('sources', [])
            for source in sources:
                if 'type' not in source or 'fields' not in source:
                    print(f"Warning: Thermal source missing required fields: {source.get('name', 'unnamed')}")
                    valid = False
        
        # Validate species sources
        if self.species_sources.get('enabled', False):
            sources = self.species_sources.get('sources', [])
            for source in sources:
                if 'type' not in source or 'fields' not in source:
                    print(f"Warning: Species source missing required fields: {source.get('name', 'unnamed')}")
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

    def _write_source_section(self, section_name, sources_dict):
        """
        Write a source section (momentum sources, thermal sources, etc.).

        Args:
            section_name (str): Name of the source section.
            sources_dict (dict): Dictionary containing source configurations.
        """
        if not sources_dict.get('enabled', False):
            return
            
        sources = sources_dict.get('sources', [])
        if not sources:
            return
            
        for source in sources:
            source_name = source.get('name', 'unnamed')
            self.file_handle.write(f"{source_name}\n")
            self.file_handle.write("{\n")
            
            # Write source properties
            for key, value in source.items():
                if key != 'name':
                    if isinstance(value, dict):
                        self.file_handle.write(f"    {key}\n")
                        self.file_handle.write("    {\n")
                        self._write_dict_recursively(value, indent_level=2)
                        self.file_handle.write("    }\n")
                    elif isinstance(value, (list, tuple)):
                        if isinstance(value, list) and value and isinstance(value[0], str):
                            val_str = ' '.join([f'"{v}"' for v in value])
                        else:
                            val_str = ' '.join(map(str, value))
                        self.file_handle.write(f"    {key:<20} ({val_str});\n")
                    elif isinstance(value, bool):
                        val_str = "true" if value else "false"
                        self.file_handle.write(f"    {key:<20} {val_str};\n")
                    else:
                        self.file_handle.write(f"    {key:<20} {value};\n")
            
            self.file_handle.write("}\n\n")

    def _write_properties(self):
        """Writes the main content of the fvOptions file."""
        self._write_source_section("Momentum Sources", self.momentum_sources)
        self._write_source_section("Thermal Sources", self.thermal_sources)
        self._write_source_section("Species Sources", self.species_sources)
        self._write_source_section("Turbulence Sources", self.turbulence_sources)
        self._write_source_section("Pressure Sources", self.pressure_sources)
        self._write_source_section("Volume Fraction Sources", self.volume_fraction_sources)
        self._write_source_section("Advanced Sources", self.advanced_sources)

    def write(self):
        """
        Writes the complete fvOptions file.
        """
        print(f"Writing fvOptions to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
