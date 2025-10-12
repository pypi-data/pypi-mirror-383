# Create a wrapper function that handles Windows properly
# ! pip install solidpython2 jupyterscad
from solid2 import *
import tempfile
import os
from jupyterscad import view #
openscad="C:\Program Files\OpenSCAD\openscad.exe"
def view3d(obj, width=600, height=600, openscad_exec=openscad):
    # Create temp file with delete=False
    scad_tmp = tempfile.NamedTemporaryFile(suffix=".scad", delete=False, mode='w')
    stl_tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
    
    try:
        # Write the OpenSCAD code
        scad_tmp.write(str(obj))
        scad_tmp.close()
        
        # Render STL
        from jupyterscad._render import process
        process(scad_tmp.name, stl_tmp.name, executable=openscad_exec)
        
        # View the STL
        from jupyterscad._view import view_stl
        result = view_stl(stl_tmp.name, width=width, height=height)
        
        return result
    finally:
        # Clean up temp files
        try:
            os.unlink(scad_tmp.name)
        except:
            pass
        try:
            os.unlink(stl_tmp.name)
        except:
            pass

# Use the wrapper function

# view3d(d, width=600, height=600, openscad_exec=openscad)