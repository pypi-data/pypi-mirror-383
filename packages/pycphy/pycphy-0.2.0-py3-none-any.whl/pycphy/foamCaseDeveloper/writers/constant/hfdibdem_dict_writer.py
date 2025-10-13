# hfdibdem_dict_writer.py

from ..foam_writer import FoamWriter

class HFDIBDEMDictWriter(FoamWriter):
    """
    A class to write an OpenFOAM HFDIBDEMDict file.

    Handles complex, nested structures and dynamic body definitions
    by recursively processing a complete property dictionary.
    """

    def __init__(self, file_path, properties):
        """
        Initializes the HFDIBDEMDictWriter.

        Args:
            file_path (str): The full path to the output file 'constant/HFDIBDEMDict'.
            properties (dict): A dictionary containing the full content of the file.
        """
        # Note: location is "constant" for this file type.
        super().__init__(file_path, foam_class="dictionary", foam_object="HFDIBDEMDict")
        self.properties = properties

    def _write_recursively(self, data, indent_level):
        """
        Recursively writes dictionary contents, handling nested dictionaries,
        lists, and tuples (vectors/tensors).
        """
        indent = "    " * indent_level
        
        # Pre-calculate padding for neat alignment
        keys_to_pad = [k for k, v in data.items() if not isinstance(v, dict)]
        max_key_len = max((len(k) for k in keys_to_pad), default=0)

        for key, value in data.items():
            if isinstance(value, dict):
                # Write a sub-dictionary
                self.file_handle.write(f"\n{indent}{key}\n")
                self.file_handle.write(f"{indent}{{\n")
                self._write_recursively(value, indent_level + 1)
                self.file_handle.write(f"{indent}}}\n")
            elif isinstance(value, (list, tuple)):
                # Write a list or vector: (item1 item2 ...)
                # Check if it's a list of strings (like bodyNames) to add quotes
                if isinstance(value, list) and value and isinstance(value[0], str):
                    # Quote string items: ("body1" "body2")
                    val_str = ' '.join([f'"{v}"' for v in value])
                else:
                    # Standard numbers/vectors: (1 0 0)
                    val_str = ' '.join(map(str, value))
                
                self.file_handle.write(f"{indent}{key:<{max_key_len}} ({val_str});\n")
            elif isinstance(value, bool):
                # Write booleans as 'true' or 'false'
                val_str = "true" if value else "false"
                self.file_handle.write(f"{indent}{key:<{max_key_len}} {val_str};\n")
            else:
                # Write simple key-value pairs (numbers, strings with units)
                self.file_handle.write(f"{indent}{key:<{max_key_len}} {value};\n")

    def _write_properties(self):
        """Writes the main content of the HFDIBDEMDict file."""
        self._write_recursively(self.properties, indent_level=0)
        
    def write(self):
        """Writes the complete file."""
        print(f"Writing HFDIBDEMDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            # Note: This file type often has 'location "constant";' in header.
            # The base FoamWriter handles class/object. 
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")