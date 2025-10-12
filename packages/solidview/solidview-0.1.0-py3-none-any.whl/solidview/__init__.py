"""
SolidView - A Python package for 3D visualization of SolidPython2 objects.

This package provides utilities to visualize 3D objects created with SolidPython2
in Jupyter notebooks using OpenSCAD rendering and JupyterSCAD visualization.
"""

__version__ = "0.1.0"
__author__ = "Anicet Cyrille Kambou"
__email__ = "kanicetcyrille@gmail.com"

from .viewer import view3d, SolidViewer

__all__ = ["view3d", "SolidViewer"]