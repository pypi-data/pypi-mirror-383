# control_dict_writer.py

from ..foam_writer import FoamWriter

class ControlDictWriter(FoamWriter):
    """
    A class to write an OpenFOAM controlDict file.

    It takes a dictionary of control parameters and formats them
    into a valid controlDict file.
    """

    def __init__(self, file_path, params):
        """
        Initializes the ControlDictWriter.

        Args:
            file_path (str): The full path to the output file 'controlDict'.
            params (dict): A dictionary containing the key-value pairs for the controlDict.
                           e.g., {'application': 'icoFoam', 'deltaT': 0.001}
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="controlDict")
        self.params = params
    
    def validate_params(self):
        """
        Validates the control parameters for common issues.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        required_params = ['application', 'startFrom', 'stopAt']
        
        for param in required_params:
            if param not in self.params:
                print(f"Warning: Required parameter '{param}' is missing from control parameters.")
                return False
        
        # Validate application
        valid_applications = [
            'icoFoam', 'simpleFoam', 'pimpleFoam', 'interFoam', 
            'rhoSimpleFoam', 'rhoPimpleFoam', 'buoyantFoam'
        ]
        
        if self.params.get('application') not in valid_applications:
            print(f"Warning: Application '{self.params.get('application')}' may not be a valid OpenFOAM solver.")
        
        # Validate time step
        if 'deltaT' in self.params:
            try:
                delta_t = float(self.params['deltaT'])
                if delta_t <= 0:
                    print("Warning: deltaT should be positive.")
                    return False
            except (ValueError, TypeError):
                print("Warning: deltaT should be a valid number.")
                return False
        
        return True

    def _write_parameters(self):
        """Writes the control parameters from the dictionary."""
        # Find the longest key for alignment purposes to make the file pretty
        max_key_len = max(len(key) for key in self.params.keys()) if self.params else 0
        padding = max_key_len + 4 # Add some extra space

        for key, value in self.params.items():
            # The format string left-aligns the key in a padded field
            line = f"{key:<{padding}} {value};\n"
            self.file_handle.write(line)
        self.file_handle.write("\n")


    def write(self):
        """
        Writes the complete controlDict file.
        """
        print(f"Writing controlDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            # Write controlDict specific content
            self._write_parameters()

            self._write_footer()
        self.file_handle = None
        print("...Done")
