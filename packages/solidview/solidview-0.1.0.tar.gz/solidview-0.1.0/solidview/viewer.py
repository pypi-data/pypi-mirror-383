"""
Core viewer module for SolidView package.

This module provides the main functionality for rendering and viewing 3D objects
created with SolidPython2.
"""

import tempfile
import os
import platform
from pathlib import Path
from typing import Optional, Union, Any

try:
    from solid2 import *
except ImportError:
    raise ImportError(
        "solidpython2 is required. Install it with: pip install solidpython2"
    )

try:
    from jupyterscad import view
    from jupyterscad._render import process
    from jupyterscad._view import view_stl
except ImportError:
    raise ImportError(
        "jupyterscad is required. Install it with: pip install jupyterscad"
    )


class SolidViewer:
    """
    A class for viewing 3D objects created with SolidPython2.
    
    This class provides methods to render SolidPython2 objects into STL files
    and display them in Jupyter notebooks using JupyterSCAD.
    """
    
    def __init__(self, openscad_exec: Optional[str] = None):
        """
        Initialize the SolidViewer.
        
        Args:
            openscad_exec: Path to OpenSCAD executable. If None, attempts to
                          find it automatically based on the operating system.
        """
        self.openscad_exec = openscad_exec or self._find_openscad()
    
    def _find_openscad(self) -> str:
        """
        Attempt to find OpenSCAD executable automatically.
        
        Returns:
            Path to OpenSCAD executable.
            
        Raises:
            FileNotFoundError: If OpenSCAD is not found.
        """
        system = platform.system().lower()
        
        if system == "windows":
            possible_paths = [
                r"C:\Program Files\OpenSCAD\openscad.exe",
                r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
            ]
        elif system == "darwin":  # macOS
            possible_paths = [
                "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
            ]
        else:  # Linux and others
            possible_paths = [
                "/usr/bin/openscad",
                "/usr/local/bin/openscad",
            ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        
        # Try to find in PATH
        import shutil
        path_exec = shutil.which("openscad")
        if path_exec:
            return path_exec
            
        raise FileNotFoundError(
            "OpenSCAD executable not found. Please install OpenSCAD or "
            "provide the path manually when creating SolidViewer instance."
        )
    
    def view(
        self, 
        obj: Any, 
        width: int = 600, 
        height: int = 600,
        cleanup: bool = True
    ) -> Any:
        """
        Render and view a 3D object.
        
        Args:
            obj: SolidPython2 object to render
            width: Width of the viewer in pixels
            height: Height of the viewer in pixels
            cleanup: Whether to clean up temporary files after viewing
            
        Returns:
            JupyterSCAD viewer result
            
        Raises:
            RuntimeError: If rendering fails
        """
        # Create temporary files
        scad_tmp = tempfile.NamedTemporaryFile(
            suffix=".scad", delete=False, mode='w'
        )
        stl_tmp = tempfile.NamedTemporaryFile(
            suffix=".stl", delete=False
        )
        
        try:
            # Write the OpenSCAD code
            scad_tmp.write(str(obj))
            scad_tmp.close()
            
            # Render STL
            process(scad_tmp.name, stl_tmp.name, executable=self.openscad_exec)
            
            # View the STL
            result = view_stl(stl_tmp.name, width=width, height=height)
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to render object: {str(e)}")
            
        finally:
            # Clean up temporary files if requested
            if cleanup:
                self._cleanup_files([scad_tmp.name, stl_tmp.name])
    
    def _cleanup_files(self, file_paths: list) -> None:
        """
        Clean up temporary files.
        
        Args:
            file_paths: List of file paths to remove
        """
        for file_path in file_paths:
            try:
                os.unlink(file_path)
            except (OSError, FileNotFoundError):
                # File might already be deleted or permission error
                pass
    
    def save_stl(
        self, 
        obj: Any, 
        output_path: Union[str, Path],
        overwrite: bool = False
    ) -> str:
        """
        Render an object and save it as an STL file.
        
        Args:
            obj: SolidPython2 object to render
            output_path: Path where to save the STL file
            overwrite: Whether to overwrite existing files
            
        Returns:
            Path to the saved STL file
            
        Raises:
            FileExistsError: If file exists and overwrite is False
            RuntimeError: If rendering fails
        """
        output_path = Path(output_path)
        
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"File {output_path} already exists")
        
        # Create temporary SCAD file
        scad_tmp = tempfile.NamedTemporaryFile(
            suffix=".scad", delete=False, mode='w'
        )
        
        try:
            # Write the OpenSCAD code
            scad_tmp.write(str(obj))
            scad_tmp.close()
            
            # Render STL directly to output path
            process(scad_tmp.name, str(output_path), executable=self.openscad_exec)
            
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save STL: {str(e)}")
            
        finally:
            # Clean up temporary SCAD file
            self._cleanup_files([scad_tmp.name])


# Create a default viewer instance
_default_viewer = None


def view3d(
    obj: Any, 
    width: int = 600, 
    height: int = 600, 
    openscad_exec: Optional[str] = None
) -> Any:
    """
    Render and view a 3D object (convenience function).
    
    This is a convenience function that creates a SolidViewer instance
    and calls its view method. For repeated use, consider creating a
    SolidViewer instance directly for better performance.
    
    Args:
        obj: SolidPython2 object to render
        width: Width of the viewer in pixels
        height: Height of the viewer in pixels
        openscad_exec: Path to OpenSCAD executable
        
    Returns:
        JupyterSCAD viewer result
    """
    global _default_viewer
    
    if _default_viewer is None or openscad_exec is not None:
        _default_viewer = SolidViewer(openscad_exec)
    
    return _default_viewer.view(obj, width, height)