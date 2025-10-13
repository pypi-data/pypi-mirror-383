# foam_writer.py

import os
from datetime import datetime

class FoamWriter:
    """
    A base class for writing OpenFOAM dictionary files.
    
    This class handles the creation of the standard OpenFOAM header,
    FoamFile dictionary, and footer comments. It is intended to be
    inherited by more specific writer classes.
    """

    def __init__(self, file_path, foam_class, foam_object):
        """
        Initializes the FoamWriter.
        
        Args:
            file_path (str): The full path to the output file.
            foam_class (str): The 'class' entry for the FoamFile dictionary (e.g., 'dictionary').
            foam_object (str): The 'object' entry for the FoamFile dictionary (e.g., 'blockMeshDict').
        """
        self.file_path = file_path
        self.foam_class = foam_class
        self.foam_object = foam_object
        self.file_handle = None
        
        # Ensure the directory exists
        dir_name = os.path.dirname(self.file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    def _write_header(self):
        """Writes the standard C++ style OpenFOAM header."""
        header = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v{version}                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
""".format(version=datetime.now().strftime("%y%m")) # e.g., v2312
        self.file_handle.write(header)

    def _write_foamfile_dict(self):
        """Writes the FoamFile dictionary section."""
        foam_dict = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {self.foam_class};
    object      {self.foam_object};
}}
"""
        self.file_handle.write(foam_dict)

    def _write_separator(self):
        """Writes a standard separator line."""
        self.file_handle.write("//" + "*" * 79 + "//\n\n")

    def _write_footer(self):
        """Writes the standard footer line."""
        self.file_handle.write("\n//" + "*" * 79 + "//\n")

    def write(self):
        """
        Main writing method. This should be overridden by child classes.
        
        This method sets up the file and writes the common header and footer,
        but the main content writing is left to the inheriting class.
        """
        raise NotImplementedError("The 'write' method must be implemented by a subclass.")
