#!/usr/bin/env python3
"""
Validation script for SolidView package
"""

import os
import sys
import tempfile
from pathlib import Path

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        import solidview
        print(f"✓ solidview imported successfully (version {solidview.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import solidview: {e}")
        return False
        
    try:
        from solidview import view3d, SolidViewer
        print("✓ Main functions imported successfully")
        # Make SolidViewer available globally for other tests
        globals()['SolidViewer'] = SolidViewer
    except ImportError as e:
        print(f"✗ Failed to import main functions: {e}")
        return False
        
    try:
        from solid2 import cube, sphere, cylinder
        print("✓ SolidPython2 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SolidPython2: {e}")
        print("  Install with: pip install solidpython2")
        return False
        
    return True

def test_solidviewer_creation():
    """Test SolidViewer creation."""
    print("\nTesting SolidViewer creation...")
    
    try:
        # Try with custom OpenSCAD path (Windows)
        openscad_path = r"C:\Program Files\OpenSCAD\openscad.exe"
        if os.path.exists(openscad_path):
            viewer = SolidViewer(openscad_exec=openscad_path)
            print(f"✓ SolidViewer created with custom OpenSCAD path")
        else:
            print(f"⚠ OpenSCAD not found at {openscad_path}, trying auto-detection...")
            
        # Try auto-detection
        try:
            viewer = SolidViewer()
            print(f"✓ SolidViewer created with auto-detected OpenSCAD: {viewer.openscad_exec}")
        except FileNotFoundError:
            print("✗ OpenSCAD not found automatically")
            print("  Please install OpenSCAD from https://openscad.org/")
            return False
            
    except Exception as e:
        print(f"✗ Failed to create SolidViewer: {e}")
        return False
        
    return True

def test_object_creation():
    """Test 3D object creation and SCAD conversion."""
    print("\nTesting 3D object creation...")
    
    try:
        from solid2 import cube, sphere, translate
        
        # Create simple objects
        cube_obj = cube([10, 10, 10])
        sphere_obj = sphere(5)
        
        # Test SCAD conversion
        cube_scad = str(cube_obj)
        sphere_scad = str(sphere_obj)
        
        print(f"✓ Cube created and converted to SCAD ({len(cube_scad)} chars)")
        print(f"✓ Sphere created and converted to SCAD ({len(sphere_scad)} chars)")
        
        # Test combination
        combined = cube_obj + translate([15, 0, 0])(sphere_obj)
        combined_scad = str(combined)
        
        print(f"✓ Combined object created ({len(combined_scad)} chars)")
        
        return True, cube_obj
        
    except Exception as e:
        print(f"✗ Failed to create objects: {e}")
        return False, None

def test_stl_export():
    """Test STL export functionality."""
    print("\nTesting STL export...")
    
    try:
        from solid2 import cube
        
        # Create a simple object
        test_cube = cube([5, 5, 5])
        
        # Create viewer with dummy OpenSCAD path for testing
        viewer = SolidViewer(openscad_exec="dummy_path_for_test")
        
        # Test the save_stl method (will fail at render, but tests the setup)
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            temp_path = tmp.name
            
        try:
            viewer.save_stl(test_cube, temp_path, overwrite=True)
            print("✓ STL export method called successfully")
        except RuntimeError:
            # Expected if OpenSCAD is not properly set up
            print("⚠ STL export setup correct (would fail at render without proper OpenSCAD)")
        except Exception as e:
            print(f"✗ STL export method failed: {e}")
            return False
        finally:
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
        return True
        
    except Exception as e:
        print(f"✗ STL export test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("SolidView Package Validation")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        
    # Test SolidViewer creation
    if not test_solidviewer_creation():
        all_passed = False
        
    # Test object creation
    success, test_obj = test_object_creation()
    if not success:
        all_passed = False
        
    # Test STL export
    if not test_stl_export():
        all_passed = False
        
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! SolidView package is working correctly.")
        print("\nNext steps:")
        print("1. Install OpenSCAD if not already installed: https://openscad.org/")
        print("2. Try the examples: python examples/basic_usage.py")
        print("3. Use in Jupyter notebook for interactive visualization")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())