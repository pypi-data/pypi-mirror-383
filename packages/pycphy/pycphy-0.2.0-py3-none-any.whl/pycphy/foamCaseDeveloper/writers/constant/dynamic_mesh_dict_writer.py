# dynamic_mesh_dict_writer.py

from ..foam_writer import FoamWriter

class DynamicMeshDictWriter(FoamWriter):
    """
    A class to write an OpenFOAM dynamicMeshDict file.

    This writer is highly flexible and can handle the diverse and nested
    structures required for various dynamic mesh types by recursively
    processing a Python dictionary.
    """

    def __init__(self, file_path, properties):
        """
        Initializes the DynamicMeshDictWriter.

        Args:
            file_path (str): The full path to the output file 'dynamicMeshDict'.
            properties (dict): A dictionary containing the full content of the
                               dynamicMeshDict file.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="dynamicMeshDict")
        self.properties = properties

    def _write_recursively(self, data, indent_level):
        """
        Recursively writes dictionary contents, handling nested dictionaries and lists.

        Args:
            data (dict): The dictionary to write.
            indent_level (int): The current level of indentation.
        """
        indent = "    " * indent_level
        max_key_len = max((len(k) for k in data.keys()), default=0)

        for key, value in data.items():
            if isinstance(value, dict):
                # If value is a dictionary, write a new block
                self.file_handle.write(f"{indent}{key}\n")
                self.file_handle.write(f"{indent}{{\n")
                self._write_recursively(value, indent_level + 1)
                self.file_handle.write(f"{indent}}}\n")
            elif isinstance(value, list):
                # If value is a list, format as (item1 item2 ...)
                list_str = ' '.join(map(str, value))
                self.file_handle.write(f"{indent}{key:<{max_key_len}}    ({list_str});\n")
            elif isinstance(value, tuple):
                 # If value is a tuple, format as (item1 item2 ...) without quotes
                tuple_str = ' '.join(map(str, value))
                self.file_handle.write(f"{indent}{key:<{max_key_len}}    ({tuple_str});\n")
            else:
                # Otherwise, it's a simple key-value pair
                self.file_handle.write(f"{indent}{key:<{max_key_len}}    {value};\n")

    def _write_properties(self):
        """Writes the main content of the dynamicMeshDict file."""
        self._write_recursively(self.properties, indent_level=0)
        
    def write(self):
        """
        Writes the complete dynamicMeshDict file.
        """
        print(f"Writing dynamicMeshDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")