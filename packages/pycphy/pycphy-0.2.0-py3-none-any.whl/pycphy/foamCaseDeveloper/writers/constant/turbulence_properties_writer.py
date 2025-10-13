# turbulence_properties_writer.py

from ..foam_writer import FoamWriter

class TurbulencePropertiesWriter(FoamWriter):
    """
    A class to write an OpenFOAM turbulenceProperties file.

    This writer can handle the nested dictionary structures required for
    RAS and LES turbulence models.
    """

    def __init__(self, file_path, simulation_type, model_properties):
        """
        Initializes the TurbulencePropertiesWriter.

        Args:
            file_path (str): The full path to the output file 'turbulenceProperties'.
            simulation_type (str): The top-level simulation type (e.g., 'RAS', 'LES', 'laminar').
            model_properties (dict): A dictionary containing the properties for the chosen model.
                                     This dictionary can be nested.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="turbulenceProperties")
        self.simulation_type = simulation_type
        self.model_properties = model_properties
    
    def validate_simulation_type(self):
        """
        Validates the simulation type.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid_types = ['RAS', 'LES', 'laminar']
        
        if self.simulation_type not in valid_types:
            print(f"Warning: Invalid simulation type '{self.simulation_type}'. Valid types: {valid_types}")
            return False
        
        return True
    
    def validate_model_properties(self):
        """
        Validates the model properties based on simulation type.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        if self.simulation_type == 'RAS':
            required_keys = ['RASModel', 'turbulence']
            for key in required_keys:
                if key not in self.model_properties:
                    print(f"Warning: Required RAS parameter '{key}' is missing.")
                    return False
                    
            # Validate RAS model
            valid_ras_models = ['kEpsilon', 'realizableKE', 'kOmegaSST', 'SpalartAllmaras']
            if self.model_properties.get('RASModel') not in valid_ras_models:
                print(f"Warning: Unknown RAS model '{self.model_properties.get('RASModel')}'.")
        
        elif self.simulation_type == 'LES':
            required_keys = ['LESModel', 'turbulence']
            for key in required_keys:
                if key not in self.model_properties:
                    print(f"Warning: Required LES parameter '{key}' is missing.")
                    return False
                    
            # Validate LES model
            valid_les_models = ['Smagorinsky', 'kEqn', 'WALE', 'dynamicKEqn']
            if self.model_properties.get('LESModel') not in valid_les_models:
                print(f"Warning: Unknown LES model '{self.model_properties.get('LESModel')}'.")
        
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
            else:
                # Otherwise, it's a simple key-value pair
                padded_key = f"{key:<{max_key_len}}"
                self.file_handle.write(f"{indent}{padded_key}    {value};\n")

    def _write_properties(self):
        """Writes the main content of the turbulenceProperties file."""
        self.file_handle.write(f"simulationType      {self.simulation_type};\n\n")

        # Start the main model block (e.g., RAS, LES)
        # For laminar, this block is often omitted, but writing an empty one is also valid.
        if self.model_properties or self.simulation_type != "laminar":
            self.file_handle.write(f"{self.simulation_type}\n")
            self.file_handle.write("{\n")
            self._write_dict_recursively(self.model_properties, indent_level=1)
            self.file_handle.write("}\n")
        
    def write(self):
        """
        Writes the complete turbulenceProperties file.
        """
        print(f"Writing turbulenceProperties to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
