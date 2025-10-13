# block_mesh_developer.py

from ..writers.system.block_mesh_writer import BlockMeshWriter

class BlockMeshDeveloper:
    """
    A high-level class to generate data for simple geometries and write
    a blockMeshDict file. It now accepts custom patch names.
    """
    def __init__(self, p0, p1, cells, patch_names, scale=1.0):
        """
        Initializes the developer for a simple cuboid.

        Args:
            p0 (tuple): The minimum corner of the cube (x0, y0, z0).
            p1 (tuple): The maximum corner of the cube (x1, y1, z1).
            cells (tuple): Number of cells in each direction (nx, ny, nz).
            patch_names (dict): A dictionary mapping face identifiers to custom names.
                                e.g., {'minX': 'inlet', 'maxX': 'outlet', ...}
            scale (float): The scaling factor for the mesh.
        """
        self.p0 = p0
        self.p1 = p1
        self.cells = cells
        self.patch_names = patch_names
        self.scale = scale
        
        # Data structures for the writer
        self.vertices = []
        self.blocks = []
        self.boundary = []
        self.edges = [] # Empty for a simple cube

    def _generate_data(self):
        """Generates the vertex, block, and boundary data for the cube."""
        x0, y0, z0 = self.p0
        x1, y1, z1 = self.p1
        
        # 1. Generate Vertices (OpenFOAM ordering)
        self.vertices = [
            (x0, y0, z0),  # 0
            (x1, y0, z0),  # 1
            (x1, y1, z0),  # 2
            (x0, y1, z0),  # 3
            (x0, y0, z1),  # 4
            (x1, y0, z1),  # 5
            (x1, y1, z1),  # 6
            (x0, y1, z1)   # 7
        ]
        
        # 2. Generate Blocks (only one for a simple cube)
        self.blocks = [
            ('hex', [0, 1, 2, 3, 4, 5, 6, 7], self.cells, 'simpleGrading', [1, 1, 1])
        ]
        
        # 3. Generate Boundary Patches using custom names
        self.boundary = [
            {
                'name': self.patch_names.get('minX', 'minX_default'), 'type': 'patch',
                'faces': [[0, 4, 7, 3]]
            },
            {
                'name': self.patch_names.get('maxX', 'maxX_default'), 'type': 'patch',
                'faces': [[1, 2, 6, 5]]
            },
            {
                'name': self.patch_names.get('minY', 'minY_default'), 'type': 'patch',
                'faces': [[0, 1, 5, 4]]
            },
            {
                'name': self.patch_names.get('maxY', 'maxY_default'), 'type': 'patch',
                'faces': [[2, 3, 7, 6]]
            },
            {
                'name': self.patch_names.get('minZ', 'minZ_default'), 'type': 'patch',
                'faces': [[0, 3, 2, 1]]
            },
            {
                'name': self.patch_names.get('maxZ', 'maxZ_default'), 'type': 'patch',
                'faces': [[4, 5, 6, 7]]
            }
        ]
        
    def create_blockmesh_dict(self, file_path):
        """
        Generates the geometry data and writes the blockMeshDict file.
        
        Args:
            file_path (str): The location to save the blockMeshDict file.
        """
        self._generate_data()
        
        writer = BlockMeshWriter(
            file_path=file_path,
            scale=1.0, # Scale is typically 1 when specifying absolute coords
            vertices=self.vertices,
            blocks=self.blocks,
            edges=self.edges,
            boundary=self.boundary
        )
        writer.write()
