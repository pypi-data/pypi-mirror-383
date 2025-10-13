# snappy_hex_mesh_writer.py

import os
from typing import Dict, Any, List, Optional
from ..foam_writer import FoamWriter

class SnappyHexMeshWriter(FoamWriter):
    """
    A writer class for OpenFOAM 'snappyHexMeshDict' files.
    Handles complex mesh generation with geometry snapping and boundary layers.
    """

    def __init__(self, file_path: str, geometry: Dict[str, Any],
                 castellated_mesh_controls: Dict[str, Any],
                 snap_controls: Dict[str, Any],
                 add_layers_controls: Optional[Dict[str, Any]] = None,
                 mesh_quality_controls: Optional[Dict[str, Any]] = None,
                 merged_patches: Optional[List[str]] = None,
                 write_flags: Optional[Dict[str, Any]] = None):
        """
        Initializes the SnappyHexMeshWriter.

        Args:
            file_path (str): The full path to the snappyHexMeshDict file.
            geometry (Dict[str, Any]): Dictionary containing geometry definitions.
            castellated_mesh_controls (Dict[str, Any]): Controls for initial mesh generation.
            snap_controls (Dict[str, Any]): Controls for mesh snapping to geometry.
            add_layers_controls (Optional[Dict[str, Any]]): Controls for boundary layer generation.
            mesh_quality_controls (Optional[Dict[str, Any]]): Controls for mesh quality optimization.
            merged_patches (Optional[List[str]]): List of patches to be merged.
            write_flags (Optional[Dict[str, Any]]): Control what files are written.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="snappyHexMeshDict")
        self.geometry = geometry
        self.castellated_mesh_controls = castellated_mesh_controls
        self.snap_controls = snap_controls
        self.add_layers_controls = add_layers_controls or {}
        self.mesh_quality_controls = mesh_quality_controls or {}
        self.merged_patches = merged_patches or []
        self.write_flags = write_flags or {}

    def write(self) -> None:
        """
        Writes the snappyHexMeshDict to the specified file.
        """
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()

            # Write geometry
            f.write("geometry\n")
            f.write("{\n")
            self._write_dict_recursively(f, self.geometry, indent_level=1)
            f.write("};\n\n")

            # Write castellated mesh controls
            f.write("castellatedMeshControls\n")
            f.write("{\n")
            self._write_dict_recursively(f, self.castellated_mesh_controls, indent_level=1)
            f.write("};\n\n")

            # Write snap controls
            f.write("snapControls\n")
            f.write("{\n")
            self._write_dict_recursively(f, self.snap_controls, indent_level=1)
            f.write("};\n\n")

            # Write add layers controls (if provided)
            if self.add_layers_controls:
                f.write("addLayersControls\n")
                f.write("{\n")
                self._write_dict_recursively(f, self.add_layers_controls, indent_level=1)
                f.write("};\n\n")

            # Write mesh quality controls
            if self.mesh_quality_controls:
                f.write("meshQualityControls\n")
                f.write("{\n")
                self._write_dict_recursively(f, self.mesh_quality_controls, indent_level=1)
                f.write("};\n\n")

            # Write merged patches (if any)
            if self.merged_patches:
                f.write("mergePatchPairs\n")
                f.write("(\n")
                for patch in self.merged_patches:
                    f.write(f"    {patch}\n")
                f.write(");\n\n")

            # Write flags
            if self.write_flags:
                self._write_dict_recursively(f, self.write_flags, indent_level=0)

            self._write_footer()

    def _write_dict_recursively(self, f, data_dict: Dict[str, Any], indent_level: int) -> None:
        """
        Recursively writes dictionary contents to the file with proper indentation.
        """
        indent = "    " * indent_level
        for key, value in data_dict.items():
            if isinstance(value, dict):
                f.write(f"{indent}{key}\n")
                f.write(f"{indent}{{\n")
                self._write_dict_recursively(f, value, indent_level + 1)
                f.write(f"{indent}}}\n")
            elif isinstance(value, (list, tuple)):
                if isinstance(value[0], dict):
                    # Handle list of dictionaries (e.g., features)
                    f.write(f"{indent}{key}\n")
                    f.write(f"{indent}(\n")
                    for item in value:
                        f.write(f"{indent}    {{\n")
                        self._write_dict_recursively(f, item, indent_level + 2)
                        f.write(f"{indent}    }}\n")
                    f.write(f"{indent});\n")
                else:
                    # Handle simple lists/tuples
                    f.write(f"{indent}{key} (")
                    f.write(" ".join(map(str, value)))
                    f.write(");\n")
            else:
                f.write(f"{indent}{key} {value};\n")
