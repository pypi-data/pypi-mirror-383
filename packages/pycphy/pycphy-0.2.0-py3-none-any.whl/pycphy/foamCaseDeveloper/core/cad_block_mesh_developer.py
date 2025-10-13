"""
CAD-based Block Mesh Developer

This module provides functionality to generate blockMeshDict files from AutoCAD CAD files
by reading 3DSOLID and REGION entities with XData containing mesh configuration information.
"""

import os
import csv
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

from ..writers.system.block_mesh_writer import BlockMeshWriter
from ..utils.myAutoCAD import myAutoCAD


class CADBlockMeshDeveloper:
    """
    A class to generate blockMeshDict files from AutoCAD CAD files.
    
    This class reads 3DSOLID entities for block definitions and REGION entities for 
    patch definitions, using XData to identify and configure the mesh parameters.
    """
    
    def __init__(self, 
                 blocks_csv_file: str = "Inputs/blocks.csv",
                 patches_csv_file: str = "Inputs/patches.csv",
                 tolerance: float = 1e-6,
                 block_xdata_app_name: str = "BLOCKDATA",
                 region_xdata_app_name: str = "REGIONDATA"):
        """
        Initialize the CAD Block Mesh Developer.
        
        Args:
            blocks_csv_file: Path to CSV file containing block parameters
            patches_csv_file: Path to CSV file containing patch definitions
            tolerance: Tolerance for face coincidence checking
            block_xdata_app_name: XData application name for 3DSOLID entities
            region_xdata_app_name: XData application name for REGION entities
        """
        self.blocks_csv_file = blocks_csv_file
        self.patches_csv_file = patches_csv_file
        self.tolerance = tolerance
        self.block_xdata_app_name = block_xdata_app_name
        self.region_xdata_app_name = region_xdata_app_name
        
        # Data structures for mesh generation
        self.all_vertices = []
        self.block_definitions = []
        self.patch_definitions = {}
        self.solid_data = {}
        
        # Configuration data
        self.block_parameters = {}
        self.patch_info = {}
        
        # CAD connection
        self.cad_app = None
        self.modelspace = None

    def _load_csv_data(self, filepath: str, required_columns: List[str], key_column: str) -> Optional[Dict]:
        """
        Load data from a CSV file into a dictionary.
        
        Args:
            filepath: Path to the CSV file
            required_columns: List of required column names
            key_column: Column to use as dictionary key
            
        Returns:
            Dictionary with loaded data or None if error
        """
        data = {}
        try:
            with open(filepath, mode='r', newline='') as infile:
                reader = csv.DictReader(infile)
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = set(required_columns) - set(reader.fieldnames)
                    raise KeyError(f"CSV file '{filepath}' is missing required columns: {missing}")
                for row in reader:
                    key = row[key_column]
                    data[key] = row
            print(f"Successfully loaded {len(data)} definitions from '{filepath}'.")
            return data
        except FileNotFoundError:
            print(f"Error: The file '{filepath}' was not found.")
            return None
        except KeyError as e:
            print(f"Error: {e}")
            return None

    def _generate_solid_faces(self, vertex_indices: List[int]) -> List[List[int]]:
        """
        Generate face definitions for a hex block from vertex indices.
        
        Args:
            vertex_indices: List of 8 vertex indices in OpenFOAM ordering
            
        Returns:
            List of face definitions as lists of vertex indices
        """
        return [
            # Bottom face (z=0)
            [vertex_indices[0], vertex_indices[1], vertex_indices[2], vertex_indices[3]],
            # Top face (z=1)
            [vertex_indices[4], vertex_indices[5], vertex_indices[6], vertex_indices[7]],
            # Side faces
            [vertex_indices[0], vertex_indices[4], vertex_indices[7], vertex_indices[3]],  # x=0
            [vertex_indices[1], vertex_indices[2], vertex_indices[6], vertex_indices[5]],  # x=1
            [vertex_indices[0], vertex_indices[1], vertex_indices[5], vertex_indices[4]],  # y=0
            [vertex_indices[3], vertex_indices[7], vertex_indices[6], vertex_indices[2]]   # y=1
        ]

    def connect_to_cad(self) -> bool:
        """
        Connect to AutoCAD and initialize the modelspace.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.cad_app = myAutoCAD(create_if_not_exists=False)
            self.modelspace = self.cad_app.model
            return True
        except Exception as e:
            print(f"Error: Failed to connect to AutoCAD. Details: {e}")
            return False

    def load_configuration(self) -> bool:
        """
        Load block and patch configuration from CSV files.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        # Load block parameters
        self.block_parameters = self._load_csv_data(
            self.blocks_csv_file,
            ['BlockID', 'CellsX', 'CellsY', 'CellsZ', 'Grading'],
            'BlockID'
        )
        
        # Load patch information
        self.patch_info = self._load_csv_data(
            self.patches_csv_file,
            ['RegionName', 'PatchName', 'PatchType'],
            'RegionName'
        )
        
        if not self.block_parameters or not self.patch_info:
            print("Aborting due to missing or invalid configuration files.")
            return False
        
        return True

    def debug_entities(self) -> None:
        """Debug method to list all entities and their XData."""
        print("\n=== DEBUG: Listing all entities ===")
        
        entity_types = {}
        for entity in self.modelspace:
            entity_type = entity.ObjectName
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            
            # Try to get XData applications
            xdata_apps = self.cad_app.list_entity_xdata(entity)
            entity_info = {
                'handle': entity.Handle,
                'xdata_apps': xdata_apps
            }
            entity_types[entity_type].append(entity_info)
        
        for entity_type, entities in entity_types.items():
            print(f"\n{entity_type} entities ({len(entities)}):")
            for entity_info in entities:
                print(f"  Handle: {entity_info['handle']}")
                if entity_info['xdata_apps']:
                    print(f"    XData apps: {entity_info['xdata_apps']}")
                    # Show detailed XData for debugging
                    try:
                        entity = self.modelspace.HandleToObject(entity_info['handle'])
                        all_xdata = self.cad_app.get_xdata(entity, "")
                        if all_xdata:
                            self.cad_app.print_xdata(all_xdata)
                    except AttributeError:
                        # HandleToObject might not be available, skip detailed XData display
                        print(f"    (Detailed XData display not available)")
                else:
                    print(f"    No XData found")

    def process_solids(self) -> None:
        """Process 3DSOLID entities and extract block definitions."""
        print("\nProcessing 3D Solids based on XData...")
        
        for entity in self.modelspace:
            if entity.ObjectName == 'AcDb3dSolid':
                print(f"  Found 3DSOLID entity: {entity.Handle}")
                xdata = self.cad_app.get_xdata(entity, self.block_xdata_app_name)
                if xdata is None:
                    print(f"    No XData found for app '{self.block_xdata_app_name}'")
                    continue
                else:
                    print(f"    Found XData: {xdata}")
                
                try:
                    # Use the new parsing method
                    block_data = self.cad_app.get_blockdata_from_3dsolid(entity)
                    if not block_data:
                        print(f"    Could not parse block data from XData")
                        continue
                    
                    block_id = block_data.get('block_id')
                    description = block_data.get('description', "")
                    
                    if block_id in self.block_parameters:
                        props = self.block_parameters[block_id]
                        verts = self.cad_app.get_solid_vertices(entity)
                        if verts is None:
                            print(f"    Could not extract vertices from 3DSOLID entity")
                            continue
                        vert_indices = [len(self.all_vertices) + i for i in range(len(verts))]
                        self.all_vertices.extend(verts)
                        
                        # Create block definition
                        block_def = {
                            "id": block_id,
                            "vertices": tuple(vert_indices),
                            "cells": (int(props['CellsX']), int(props['CellsY']), int(props['CellsZ'])),
                            "grading": props['Grading']
                        }
                        self.block_definitions.append(block_def)
                        
                        # Generate faces for patch matching
                        faces = self._generate_solid_faces(vert_indices)
                        face_coords = [np.array([self.all_vertices[i] for i in face]) for face in faces]
                        
                        self.solid_data[entity.Handle] = {
                            "block_id": block_id,
                            "vertex_indices": vert_indices,
                            "faces_v_indices": faces,
                            "faces_v_coords": face_coords
                        }
                        
                        print(f"  Found and processed block with ID: '{block_id}'.")
                    else:
                        print(f"  Found block ID '{block_id}' but it's not defined in '{self.blocks_csv_file}'. Skipping.")
                        
                except (IndexError, KeyError, ValueError) as e:
                    print(f"  Error processing solid entity: {e}")
                    continue

    def process_regions(self) -> None:
        """Process REGION entities and match them to solid faces for patches."""
        print("\nProcessing Regions for patches based on XData...")
        
        for entity in self.modelspace:
            if entity.ObjectName == 'AcDbRegion':
                print(f"  Found REGION entity: {entity.Handle}")
                xdata = self.cad_app.get_xdata(entity, self.region_xdata_app_name)
                if xdata is None:
                    print(f"    No XData found for app '{self.region_xdata_app_name}'")
                    continue
                else:
                    print(f"    Found XData: {xdata}")
                
                try:
                    # Use the new parsing method
                    region_data = self.cad_app.get_regionname_from_region(entity)
                    if not region_data:
                        print(f"    Could not parse region data from XData")
                        continue
                    
                    region_name = region_data.get('region_name')
                    
                    if region_name in self.patch_info:
                        patch_config = self.patch_info[region_name]
                        patch_name = patch_config['PatchName']
                        
                        region_verts = self.cad_app.get_region_vertices(entity)
                        if region_verts is None:
                            print(f"    Could not extract vertices from REGION entity")
                            continue
                        match_found = False
                        
                        # Try to match region to a solid face
                        for handle, data in self.solid_data.items():
                            for i, solid_face_coords in enumerate(data['faces_v_coords']):
                                if self.cad_app.are_faces_coincident(region_verts, solid_face_coords, self.tolerance):
                                    if patch_name not in self.patch_definitions:
                                        self.patch_definitions[patch_name] = {
                                            'type': patch_config['PatchType'],
                                            'faces': []
                                        }
                                    self.patch_definitions[patch_name]['faces'].append(data['faces_v_indices'][i])
                                    print(f"  Matched region '{region_name}' to a face on block '{data['block_id']}' -> Patch: '{patch_name}'")
                                    match_found = True
                                    break
                            if match_found:
                                break
                        
                        if not match_found:
                            print(f"  WARNING: Region '{region_name}' was found but could not be matched to any solid face.")
                    else:
                        print(f"  Found region '{region_name}' but it's not defined in '{self.patches_csv_file}'. Skipping.")
                        
                except (IndexError, KeyError, ValueError) as e:
                    print(f"  Error processing region entity: {e}")
                    continue

    def _convert_to_blockmesh_format(self) -> Tuple[List, List, List]:
        """
        Convert internal data structures to BlockMeshWriter format.
        
        Returns:
            Tuple of (vertices, blocks, boundary) in BlockMeshWriter format
        """
        # Convert vertices to tuple format
        vertices = [tuple(v) for v in self.all_vertices]
        
        # Convert blocks to BlockMeshWriter format
        blocks = []
        for block in self.block_definitions:
            block_tuple = (
                'hex',
                list(block["vertices"]),
                list(block["cells"]),
                'simpleGrading',  # Default grading type
                [1, 1, 1]  # Default grading values
            )
            blocks.append(block_tuple)
        
        # Convert patches to boundary format
        boundary = []
        for name, data in sorted(self.patch_definitions.items()):
            patch_dict = {
                'name': name,
                'type': data['type'],
                'faces': data['faces']
            }
            boundary.append(patch_dict)
        
        return vertices, blocks, boundary

    def generate_blockmesh_dict(self, output_path: str = "system/blockMeshDict") -> bool:
        """
        Generate the complete blockMeshDict file from CAD data.
        
        Args:
            output_path: Path where to save the blockMeshDict file
            
        Returns:
            True if generation successful, False otherwise
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert data to BlockMeshWriter format
        vertices, blocks, boundary = self._convert_to_blockmesh_format()
        
        # Create and use the BlockMeshWriter
        writer = BlockMeshWriter(
            file_path=output_path,
            scale=1.0,
            vertices=vertices,
            blocks=blocks,
            edges=[],  # No edges for this implementation
            boundary=boundary,
            merge_patch_pairs=[]  # No merge pairs for this implementation
        )
        
        try:
            writer.write()
            print(f"Successfully generated blockMeshDict at: {output_path}")
            return True
        except Exception as e:
            print(f"Error writing blockMeshDict: {e}")
            return False
    
    def generate_zero_fields(self, output_dir: str = "0"):
        """
        Generate all zero field files using config files and CSV boundary conditions.
        
        Args:
            output_dir: Directory where to write the zero field files
        """
        from ..writers.zero.zero_field_factory import ZeroFieldFactory
        
        print("\nGenerating zero field files using config + CSV boundary conditions...")
        print("=" * 60)
        
        # Create zero field factory
        factory = ZeroFieldFactory(output_dir=output_dir)
        
        # Show available fields
        available_fields = factory.get_available_fields()
        print("Field availability:")
        for field_name, info in available_fields.items():
            print(f"  {field_name}: CSV={info['csv_available']}, BCs={len(info['boundary_conditions']) if info['boundary_conditions'] else 0} patches")
        
        # Write all zero field files
        written_fields = factory.write_all_fields(use_csv_boundaries=True)
        
        print(f"Zero field files written to: {output_dir}/")
        return written_fields

    def process_cad_file(self, output_path: str = "system/blockMeshDict", debug: bool = False) -> bool:
        """
        Complete workflow to process CAD file and generate blockMeshDict.
        
        Args:
            output_path: Path where to save the blockMeshDict file
            debug: If True, show debug information about entities and XData
            
        Returns:
            True if processing successful, False otherwise
        """
        # Step 1: Connect to CAD
        if not self.connect_to_cad():
            return False
        
        # Step 2: Load configuration
        if not self.load_configuration():
            return False
        
        # Step 2.5: Debug entities if requested
        if debug:
            self.debug_entities()
        
        # Step 3: Process solids
        self.process_solids()
        
        # Step 4: Process regions
        self.process_regions()
        
        # Step 5: Generate blockMeshDict
        success = self.generate_blockmesh_dict(output_path)
        
        if success:
            # Step 6: Generate zero field files
            self.generate_zero_fields()
            
            print("\n" + "="*60)
            print("CAD Processing Summary:")
            print("="*60)
            self.get_summary()
        
        return success

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processed data.
        
        Returns:
            Dictionary with processing summary
        """
        return {
            "total_vertices": len(self.all_vertices),
            "total_blocks": len(self.block_definitions),
            "total_patches": len(self.patch_definitions),
            "blocks": [block["id"] for block in self.block_definitions],
            "patches": list(self.patch_definitions.keys())
        }
