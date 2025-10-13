# set_fields_writer.py

"""
Set Fields Writer for OpenFOAM cases.

This writer handles the creation of setFieldsDict files with support for
initializing field values in specific regions of the domain including
cell sets, cell zones, and geometric regions.
"""

from ..foam_writer import FoamWriter


class SetFieldsWriter(FoamWriter):
    """
    A class to write an OpenFOAM setFieldsDict file.
    
    This writer supports comprehensive field initialization for various
    simulation types including multiphase flows, turbulent flows, heat transfer,
    and species transport.
    """

    def __init__(self, file_path, default_field_values=None, regions=None):
        """
        Initialize the SetFieldsWriter.

        Args:
            file_path (str): The full path to the output file 'setFieldsDict'.
            default_field_values (dict, optional): Default field values configuration.
            regions (dict, optional): Regions configuration.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="setFieldsDict")
        self.default_field_values = default_field_values or {}
        self.regions = regions or {}
    
    def validate_field_values(self):
        """
        Validate the field values configuration.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid = True
        
        # Validate default field values
        if self.default_field_values:
            fields = self.default_field_values.get('fields', [])
            for field in fields:
                if 'type' not in field or 'field' not in field or 'value' not in field:
                    print(f"Warning: Default field value missing required fields: {field}")
                    valid = False
        
        # Validate regions
        if self.regions:
            regions_list = self.regions.get('regions', [])
            for region in regions_list:
                if 'type' not in region or 'fieldValues' not in region:
                    print(f"Warning: Region missing required fields: {region.get('name', 'unnamed')}")
                    valid = False
                
                # Validate field values in region
                field_values = region.get('fieldValues', [])
                for field_value in field_values:
                    if 'type' not in field_value or 'field' not in field_value or 'value' not in field_value:
                        print(f"Warning: Field value in region missing required fields: {field_value}")
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

    def _write_field_value(self, field_value):
        """
        Write a single field value entry.

        Args:
            field_value (dict): Field value configuration.
        """
        field_type = field_value.get('type', 'volScalarFieldValue')
        field_name = field_value.get('field', 'unknown')
        field_value_val = field_value.get('value', 0.0)
        
        self.file_handle.write(f"    {field_type:<25} {field_name:<15} {field_value_val};\n")

    def _write_default_field_values(self):
        """Write default field values section."""
        if not self.default_field_values:
            return
            
        fields = self.default_field_values.get('fields', [])
        if not fields:
            return
            
        self.file_handle.write("defaultFieldValues\n")
        self.file_handle.write("(\n")
        
        for field in fields:
            self._write_field_value(field)
        
        self.file_handle.write(")\n\n")

    def _write_regions(self):
        """Write regions section."""
        if not self.regions:
            return
            
        regions_list = self.regions.get('regions', [])
        if not regions_list:
            return
            
        self.file_handle.write("regions\n")
        self.file_handle.write("(\n")
        
        for region in regions_list:
            region_name = region.get('name', 'unnamed')
            region_type = region.get('type', 'cellToCell')
            region_set = region.get('set', 'unknown')
            field_values = region.get('fieldValues', [])
            
            self.file_handle.write(f"    // {region_name}\n")
            self.file_handle.write(f"    {region_type}\n")
            self.file_handle.write("    {\n")
            self.file_handle.write(f"        set {region_set};\n\n")
            self.file_handle.write("        fieldValues\n")
            self.file_handle.write("        (\n")
            
            for field_value in field_values:
                self._write_field_value(field_value)
            
            self.file_handle.write("        );\n")
            self.file_handle.write("    }\n\n")
        
        self.file_handle.write(")\n\n")

    def _write_properties(self):
        """Writes the main content of the setFieldsDict file."""
        self._write_default_field_values()
        self._write_regions()

    def write(self):
        """
        Writes the complete setFieldsDict file.
        """
        print(f"Writing setFieldsDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            self._write_properties()

            self._write_footer()
        self.file_handle = None
        print("...Done")
