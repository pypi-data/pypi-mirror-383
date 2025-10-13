# block_mesh_writer.py

from ..foam_writer import FoamWriter

class BlockMeshWriter(FoamWriter):
    """
    A class to write OpenFOAM blockMeshDict files.

    It takes Python data structures (lists, dicts) and formats them
    into a valid blockMeshDict file.
    """

    def __init__(self, file_path, scale, vertices, blocks, edges, boundary, merge_patch_pairs=None):
        """
        Initializes the BlockMeshWriter.

        Args:
            file_path (str): The full path to the output file 'blockMeshDict'.
            scale (float): The scaling factor.
            vertices (list): A list of tuples, where each tuple is a vertex (x, y, z).
            blocks (list): A list of block definitions. Each definition is a tuple/list,
                           e.g., ('hex', [0,1,2,3,4,5,6,7], [10,10,1], 'simpleGrading', [1,1,1]).
            edges (list): A list of edge definitions (e.g., arc definitions).
            boundary (list): A list of dictionaries, where each dict defines a boundary patch.
                             e.g., {'name': 'inlet', 'type': 'patch', 'faces': [[...], [...]]}
            merge_patch_pairs (list, optional): List of pairs to merge. Defaults to an empty list.
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="blockMeshDict")
        self.scale = scale
        self.vertices = vertices
        self.blocks = blocks
        self.edges = edges
        self.boundary = boundary
        self.merge_patch_pairs = merge_patch_pairs if merge_patch_pairs is not None else []

    def _format_list_of_tuples(self, tuples):
        """Helper to format a list of tuples like vertices or faces."""
        return "\n".join([f"    ({ ' '.join(map(str, v)) })" for v in tuples])
    
    def _write_scale(self):
        """Writes the scale entry."""
        self.file_handle.write(f"scale   {self.scale};\n\n")
        
    def _write_vertices(self):
        """Writes the vertices section."""
        self.file_handle.write("vertices\n(\n")
        self.file_handle.write(self._format_list_of_tuples(self.vertices))
        self.file_handle.write("\n);\n\n")

    def _write_blocks(self):
        """Writes the blocks section."""
        self.file_handle.write("blocks\n(\n")
        for block in self.blocks:
            shape = block[0]
            verts = ' '.join(map(str, block[1]))
            cells = f"({ ' '.join(map(str, block[2])) })"
            grading_type = block[3]
            grading_vals = f"({ ' '.join(map(str, block[4])) })"
            self.file_handle.write(f"    {shape} ({verts}) {cells} {grading_type} {grading_vals}\n")
        self.file_handle.write(");\n\n")

    def _write_edges(self):
        """Writes the edges section."""
        self.file_handle.write("edges\n(\n")
        # Logic for formatting different edge types (e.g., arc) would go here
        # For now, we assume it's simple or empty.
        for edge in self.edges:
            self.file_handle.write(f"    {edge}\n")
        self.file_handle.write(");\n\n")

    def _write_boundary(self):
        """Writes the boundary section."""
        self.file_handle.write("boundary\n(\n")
        for patch in self.boundary:
            self.file_handle.write(f"    {patch['name']}\n")
            self.file_handle.write("    {\n")
            self.file_handle.write(f"        type {patch['type']};\n")
            self.file_handle.write("        faces\n")
            self.file_handle.write("        (\n")
            self.file_handle.write(self._format_list_of_tuples(patch['faces']).replace("    ", "            "))
            self.file_handle.write("\n        );\n")
            self.file_handle.write("    }\n")
        self.file_handle.write(");\n\n")

    def _write_merge_patch_pairs(self):
        """Writes the mergePatchPairs section."""
        self.file_handle.write("mergePatchPairs\n(\n")
        for pair in self.merge_patch_pairs:
             self.file_handle.write(f"    ({pair[0]} {pair[1]})\n")
        self.file_handle.write(");\n")

    def write(self):
        """
        Writes the complete blockMeshDict file by calling the section-specific methods.
        """
        print(f"Writing blockMeshDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            # Write blockMeshDict specific content
            self._write_scale()
            self._write_vertices()
            self._write_blocks()
            self._write_edges()
            self._write_boundary()
            self._write_merge_patch_pairs()

            self._write_footer()
        self.file_handle = None
        print("...Done")
