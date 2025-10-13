# transport_properties_writer.py

"""
Transport Properties Writer for OpenFOAM cases.

This writer handles the creation of transportProperties files with support for
Newtonian and non-Newtonian fluids, thermal properties, and species transport.
"""

from ..foam_writer import FoamWriter


class TransportPropertiesWriter(FoamWriter):
    """
    A class to write an OpenFOAM transportProperties file.
    
    This writer supports various transport models including Newtonian and 
    non-Newtonian fluids, thermal properties, and species transport.
    """

    def __init__(self, file_path, transport_model, model_properties, 
                 thermal_properties=None, species_properties=None, 
                 advanced_properties=None):
        """
        Initialize the TransportPropertiesWriter.

        Args:
            file_path (str): The full path to the output file 'transportProperties'.
            transport_model (str): The transport model ('Newtonian', 'NonNewtonian', etc.).
            model_properties (dict): Properties for the transport model.
            thermal_properties (dict, optional): Thermal transport properties.
            species_properties (dict, optional): Species transport properties.
            advanced_properties (dict, optional): Advanced transport properties.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="transportProperties")
        self.transport_model = transport_model
        self.model_properties = model_properties
        self.thermal_properties = thermal_properties or {}
        self.species_properties = species_properties or {}
        self.advanced_properties = advanced_properties or {}
    
    def validate_transport_model(self):
        """
        Validate the transport model.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid_models = [
            'Newtonian', 'NonNewtonian', 'BirdCarreau', 'CrossPowerLaw',
            'HerschelBulkley', 'PowerLaw', 'Casson', 'GeneralizedNewtonian'
        ]
        
        if self.transport_model not in valid_models:
            print(f"Warning: Invalid transport model '{self.transport_model}'. Valid models: {valid_models}")
            return False
        
        return True
    
    def validate_model_properties(self):
        """
        Validate the model properties based on transport model.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        if self.transport_model == 'Newtonian':
            if 'nu' not in self.model_properties:
                print("Warning: Newtonian model requires 'nu' (kinematic viscosity)")
                return False
                
        elif self.transport_model in ['NonNewtonian', 'BirdCarreau', 'CrossPowerLaw', 
                                     'HerschelBulkley', 'PowerLaw', 'Casson']:
            if 'nu' not in self.model_properties:
                print("Warning: Non-Newtonian models require 'nu' (reference viscosity)")
                return False
                
            if 'modelCoeffs' not in self.model_properties:
                print("Warning: Non-Newtonian models require 'modelCoeffs'")
                return False
        
        return True
    
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
            else:
                # Otherwise, it's a simple key-value pair
                padded_key = f"{key:<{max_key_len}}"
                self.file_handle.write(f"{indent}{padded_key}    {value};\n")

    def _write_transport_model(self):
        """Write the transport model configuration."""
        self.file_handle.write(f"transportModel      {self.transport_model};\n\n")
        
        # Write model-specific properties
        if self.transport_model == 'Newtonian':
            # Write simple Newtonian properties
            for key, value in self.model_properties.items():
                self.file_handle.write(f"{key:<20}    {value};\n")
                
        elif self.transport_model in ['NonNewtonian', 'BirdCarreau', 'CrossPowerLaw', 
                                     'HerschelBulkley', 'PowerLaw', 'Casson']:
            # Write non-Newtonian properties
            for key, value in self.model_properties.items():
                if key != 'modelCoeffs':
                    self.file_handle.write(f"{key:<20}    {value};\n")
                else:
                    # Write model coefficients as a sub-dictionary
                    self.file_handle.write(f"\n{self.transport_model}Coeffs\n")
                    self.file_handle.write("{\n")
                    self._write_dict_recursively(value, indent_level=1)
                    self.file_handle.write("}\n")
        
        self.file_handle.write("\n")

    def _write_thermal_properties(self):
        """Write thermal properties if enabled."""
        if not self.thermal_properties.get('enableThermal', False):
            return
            
        self.file_handle.write("// Thermal properties\n")
        for key, value in self.thermal_properties.items():
            if key != 'enableThermal':
                self.file_handle.write(f"{key:<20}    {value};\n")
        self.file_handle.write("\n")

    def _write_species_properties(self):
        """Write species properties if enabled."""
        if not self.species_properties.get('enableSpecies', False):
            return
            
        self.file_handle.write("// Species transport properties\n")
        for key, value in self.species_properties.items():
            if key != 'enableSpecies':
                if isinstance(value, list):
                    val_str = ' '.join(map(str, value))
                    self.file_handle.write(f"{key:<20}    ({val_str});\n")
                else:
                    self.file_handle.write(f"{key:<20}    {value};\n")
        self.file_handle.write("\n")

    def _write_advanced_properties(self):
        """Write advanced properties if enabled."""
        if not self.advanced_properties.get('enableAdvanced', False):
            return
            
        self.file_handle.write("// Advanced properties\n")
        for key, value in self.advanced_properties.items():
            if key != 'enableAdvanced':
                self.file_handle.write(f"{key:<20}    {value};\n")
        self.file_handle.write("\n")

    def _write_properties(self):
        """Writes the main content of the transportProperties file."""
        self._write_transport_model()
        self._write_thermal_properties()
        self._write_species_properties()
        self._write_advanced_properties()

    def write(self):
        """
        Writes the complete transportProperties file.
        """
        print(f"Writing transportProperties to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
