import math
import pythoncom
import numpy as np
from pyautocad import Autocad, APoint
import win32com.client
from win32com.client import VARIANT

class myAutoCAD:
    def __init__(self, create_if_not_exists=True):
        print("Connecting to AutoCAD...")
        # Use direct win32com for better COM compatibility
        try:
            self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
            self.doc = self.acad.ActiveDocument
            self.model = self.doc.ModelSpace
            print(f"Connected to: {self.doc.Name}")
        except Exception as e:
            print(f"Failed to connect to AutoCAD: {e}")
            # Fallback to pyautocad
            self.acad = Autocad(create_if_not_exists=create_if_not_exists)
            self.model = self.acad.model
            self.doc = self.acad.doc
            print(f"Connected to: {self.doc.Name}")

    def setup_layers(self, layers):
        for name, color in layers.items():
            try:
                self.doc.Layers.Item(name)
            except Exception:
                layer = self.doc.Layers.Add(name)
                layer.color = color

    @staticmethod
    def calculate_points_on_circle(center, radius, count, start_angle=0):
        points = []
        angle_step = 2 * math.pi / count
        for i in range(count):
            angle = start_angle + i * angle_step
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points

    def draw_circle(self, center, radius, color=7, layer=None):
        if layer:
            self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        circle = self.model.AddCircle(APoint(center[0], center[1]), radius)
        circle.color = color
        return circle

    def draw_text(self, position, text, height=0.1, color=7, layer=None):
        if layer:
            self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        text_obj = self.model.AddText(text, APoint(position[0], position[1]), height)
        text_obj.color = color
        return text_obj

    def zoom_extents(self):
        self.acad.app.ZoomExtents()
    
    def get_solid_vertices(self, solid_obj):
        """
        Extracts and sorts the 8 vertices of a 3DSOLID for blockMesh compatibility.
        Uses XEDGES method as reliable workaround for entities without Coordinates attribute.
        """
        try:
            # Try direct coordinates first (for entities that support it)
            try:
                coords = np.array(solid_obj.Coordinates).reshape(-1, 3)
                return self._sort_vertices_for_blockmesh(coords)
            except:
                pass
            
            # Use XEDGES method as fallback
            return self._get_vertices_via_xedges(solid_obj)
            
        except Exception as e:
            print(f"Error extracting solid vertices: {e}")
            return None

    def _sort_vertices_for_blockmesh(self, coords):
        """Sort vertices for OpenFOAM blockMesh compatibility."""
        if len(coords) == 0:
            return np.array([])
        
        # If we have exactly 8 vertices, sort them for blockMesh
        if len(coords) == 8:
            ind = np.lexsort((coords[:, 0], coords[:, 1], coords[:, 2]))
            sorted_coords = coords[ind]
            bottom_face = sorted_coords[:4]
            top_face = sorted_coords[4:]
            bottom_ind = np.lexsort((bottom_face[:, 1], bottom_face[:, 0]))
            b_temp = bottom_face[bottom_ind]
            bottom_reordered = np.array([b_temp[0], b_temp[2], b_temp[3], b_temp[1]])
            top_ind = np.lexsort((top_face[:, 1], top_face[:, 0]))
            t_temp = top_face[top_ind]
            top_reordered = np.array([t_temp[0], t_temp[2], t_temp[3], t_temp[1]])
            return np.vstack([bottom_reordered, top_reordered])
        else:
            # For other numbers of vertices (like regions), just return sorted coordinates
            print(f"    Warning: Expected 8 vertices for blockMesh, got {len(coords)}")
            ind = np.lexsort((coords[:, 0], coords[:, 1], coords[:, 2]))
            return coords[ind]

    def _get_vertices_via_xedges(self, original_solid):
        """
        Extracts 3D Solid vertices using XEDGES command on a temporary copy.
        This method is more reliable than explode and works with complex solids.
        The original solid remains completely untouched.
        """
        try:
            print(f"    Using XEDGES method...")
            
            # 1. Create a copy of the solid
            copied_solid = original_solid.Copy()
            handle = copied_solid.Handle
            print(f"    Created temporary copy (Handle: {handle})")
            
            # 2. Count entities before XEDGES
            pre_count = self.model.Count
            
            # 3. Execute XEDGES command on the copy
            self.doc.SendCommand(f'_XEDGES (handent "{handle}") \n')
            
            # 4. Gather new edges created by XEDGES
            edges = []
            for i in range(pre_count, self.model.Count):
                try:
                    edge = self.model.Item(i)
                    edges.append(edge)
                except:
                    pass
            
            print(f"    XEDGES created {len(edges)} new edges")
            
            # 5. Extract vertices from edges and clean up
            vertices_set = set()
            for edge in edges:
                try:
                    # Handle different edge types
                    if edge.ObjectName == 'AcDbLine':
                        # Simple line - has StartPoint and EndPoint
                        start_point = tuple(round(c, 8) for c in edge.StartPoint)
                        end_point = tuple(round(c, 8) for c in edge.EndPoint)
                        vertices_set.add(start_point)
                        vertices_set.add(end_point)
                    elif edge.ObjectName == 'AcDb3dPolyline':
                        # 3D Polyline - extract coordinates
                        try:
                            coords = np.array(edge.Coordinates).reshape(-1, 3)
                            for coord in coords:
                                vertex = tuple(round(c, 8) for c in coord)
                                vertices_set.add(vertex)
                        except:
                            # If Coordinates fails, try other methods
                            pass
                    elif hasattr(edge, 'StartPoint') and hasattr(edge, 'EndPoint'):
                        # Other curve types with StartPoint/EndPoint
                        start_point = tuple(round(c, 8) for c in edge.StartPoint)
                        end_point = tuple(round(c, 8) for c in edge.EndPoint)
                        vertices_set.add(start_point)
                        vertices_set.add(end_point)
                    else:
                        print(f"    Skipping unsupported edge type: {edge.ObjectName}")
                        
                except Exception as e:
                    print(f"    Error processing edge {edge.ObjectName}: {e}")
                finally:
                    # Clean up the edge immediately
                    try:
                        edge.Delete()
                    except:
                        pass
            
            # 6. Clean up the copied solid
            try:
                copied_solid.Delete()
            except:
                pass
            
            if not vertices_set:
                print("    No vertices could be extracted")
                return None
            
            # Convert to numpy array and sort for blockMesh
            vertex_list = sorted(list(vertices_set))
            coords = np.array(vertex_list)
            
            print(f"    Extracted {len(vertices_set)} unique vertices")
            return self._sort_vertices_for_blockmesh(coords)
            
        except Exception as e:
            print(f"    XEDGES method failed: {e}")
            # Try bounding box method as fallback
            return self._get_vertices_via_bounding_box(original_solid)

    def _get_vertices_via_bounding_box(self, solid_obj):
        """
        Alternative method to get vertices using bounding box.
        This creates a rectangular box approximation of the solid.
        """
        try:
            print(f"    Trying bounding box method...")
            
            # Get bounding box
            try:
                # Method 1: Direct GetBoundingBox
                min_point, max_point = solid_obj.GetBoundingBox()
            except:
                try:
                    # Method 2: Through utility
                    util = self.acad.Utility
                    min_point, max_point = util.GetBoundingBox(solid_obj)
                except:
                    try:
                        # Method 3: Manual calculation
                        min_point = [float('inf'), float('inf'), float('inf')]
                        max_point = [float('-inf'), float('-inf'), float('-inf')]
                        # This is a simplified approach - in reality we'd need more sophisticated methods
                        raise Exception("Manual bounding box not implemented")
                    except:
                        raise Exception("Could not get bounding box")
            
            # Create 8 vertices of a rectangular box
            x_min, y_min, z_min = min_point
            x_max, y_max, z_max = max_point
            
            vertices = np.array([
                [x_min, y_min, z_min],  # 0: bottom-left-back
                [x_max, y_min, z_min],  # 1: bottom-right-back
                [x_max, y_max, z_min],  # 2: bottom-right-front
                [x_min, y_max, z_min],  # 3: bottom-left-front
                [x_min, y_min, z_max],  # 4: top-left-back
                [x_max, y_min, z_max],  # 5: top-right-back
                [x_max, y_max, z_max],  # 6: top-right-front
                [x_min, y_max, z_max]   # 7: top-left-front
            ])
            
            print(f"    Created bounding box with vertices at:")
            print(f"    Min: ({x_min:.3f}, {y_min:.3f}, {z_min:.3f})")
            print(f"    Max: ({x_max:.3f}, {y_max:.3f}, {z_max:.3f})")
            
            return self._sort_vertices_for_blockmesh(vertices)
            
        except Exception as e:
            print(f"    Bounding box method failed: {e}")
            return None

    def get_region_vertices(self, region_obj):
        """Extracts the vertices of a REGION object."""
        try:
            # Try direct coordinates first
            try:
                return np.array(region_obj.Coordinates).reshape(-1, 3)
            except:
                pass
            
            # Try XEDGES method for regions as well
            return self._get_vertices_via_xedges(region_obj)
            
        except Exception as e:
            print(f"Error extracting region vertices: {e}")
            return None

    def are_faces_coincident(self, face1_verts, face2_verts, tol):
        """Checks if two faces (sets of vertices) are the same within a tolerance."""
        if face1_verts.shape != face2_verts.shape: 
            return False
        for v1 in face1_verts:
            if not np.any(np.linalg.norm(face2_verts - v1, axis=1) < tol): 
                return False
        return True

    def get_xdata(self, entity, app_name=""):
        """
        Get XData from an AutoCAD entity - SIMPLIFIED VERSION
        
        Parameters:
        entity - AutoCAD entity object
        app_name - Application name (e.g., "BLOCKDATA"). Empty string gets all xdata.
        
        Returns:
        List of tuples (type_code, value) or None if no xdata found
        """
        try:
            # Simple direct call - much cleaner!
            types, values = entity.GetXData(app_name)
            
            # Check if we got data
            if not types or not values:
                return None
            
            # Convert to tuples for easier processing
            xdata_list = []
            for i in range(len(types)):
                xdata_list.append((types[i], values[i]))
            
            return xdata_list
        
        except Exception as e:
            print(f"Error getting XData: {e}")
            return None

    def set_xdata(self, entity, app_name, data):
        """Sets XData on an AutoCAD entity."""
        try:
            entity.SetXData(app_name, data)
            return True
        except (pythoncom.com_error, TypeError, IndexError):
            return False
    
    def get_xdata_type_description(self, type_code):
        """Get human-readable description of XData type code"""
        type_map = {
            1000: "String",
            1001: "Registered App Name",
            1002: "Control String",
            1003: "Layer Name",
            1004: "Binary Data",
            1005: "Database Handle",
            1010: "3D Point",
            1011: "3D Position",
            1012: "3D Displacement",
            1013: "3D Direction",
            1040: "Real Number",
            1041: "Distance",
            1042: "Scale Factor",
            1070: "16-bit Integer",
            1071: "32-bit Integer"
        }
        return type_map.get(type_code, f"Unknown ({type_code})")

    def parse_xdata(self, xdata_list):
        """
        Parse raw xdata list into readable format
        """
        if not xdata_list:
            return None
        
        parsed = []
        for type_code, value in xdata_list:
            entry = {
                'type_code': type_code,
                'value': value,
                'description': self.get_xdata_type_description(type_code)
            }
            parsed.append(entry)
        
        return parsed

    def print_xdata(self, xdata_list):
        """Print xdata in a formatted way"""
        if not xdata_list:
            print("No XData to display")
            return
        
        print("\nXData Contents:")
        print("-" * 70)
        for i, (type_code, value) in enumerate(xdata_list):
            desc = self.get_xdata_type_description(type_code)
            print(f"[{i}] Type: {type_code} ({desc})")
            print(f"    Value: {value}")
        print("-" * 70)

    def get_blockdata_from_3dsolid(self, entity):
        """Get Block ID and Description from 3D solid with BLOCKDATA"""
        xdata = self.get_xdata(entity, "BLOCKDATA")
        
        if not xdata:
            return None
        
        # Parse the data - structure should be:
        # [0] (1001, "BLOCKDATA") - App name
        # [1] (1000, "block_id_value") - Block ID
        # [2] (1000, "description_value") - Description
        
        result = {}
        if len(xdata) > 1 and xdata[1][0] == 1000:
            result['block_id'] = xdata[1][1]
        if len(xdata) > 2 and xdata[2][0] == 1000:
            result['description'] = xdata[2][1]
        
        return result if result else None

    def get_regionname_from_region(self, entity):
        """Get Region Name from region object with REGIONDATA"""
        xdata = self.get_xdata(entity, "REGIONDATA")
        
        if not xdata:
            return None
        
        # Parse the data - structure should be:
        # [0] (1001, "REGIONDATA") - App name
        # [1] (1000, "region_name_value") - Region Name
        
        result = {}
        if len(xdata) > 1 and xdata[1][0] == 1000:
            result['region_name'] = xdata[1][1]
        
        return result if result else None

    def list_entity_xdata(self, entity):
        """Lists all XData applications for an entity (for debugging)."""
        try:
            # Get all XData first
            all_xdata = self.get_xdata(entity, "")
            if not all_xdata:
                return []
            
            # Extract application names from XData
            xdata_apps = []
            for type_code, value in all_xdata:
                if type_code == 1001:  # Registered application name
                    xdata_apps.append(value)
            
            return xdata_apps
        except:
            return []