"""
Basic SolidView Example

This example demonstrates the basic usage of SolidView for visualizing
3D objects created with SolidPython2.
"""

from solid2 import *
from solidview import view3d, SolidViewer

def basic_shapes():
    """Create and view basic 3D shapes."""
    print("Creating basic shapes...")
    
    # Simple cube
    cube_obj = cube([10, 10, 10])
    print("Viewing cube...")
    view3d(cube_obj, width=400, height=400)
    
    # Simple sphere
    sphere_obj = sphere(8)
    print("Viewing sphere...")
    view3d(sphere_obj, width=400, height=400)
    
    # Combined shapes
    combined = cube_obj + translate([15, 0, 0])(sphere_obj)
    print("Viewing combined shapes...")
    view3d(combined, width=600, height=400)

def complex_object():
    """Create a more complex object."""
    print("Creating complex object...")
    
    # Base platform
    base = cube([30, 30, 5])
    
    # Cylindrical posts
    post1 = translate([7.5, 7.5, 5])(cylinder(r=2, h=15))
    post2 = translate([22.5, 7.5, 5])(cylinder(r=2, h=15))
    post3 = translate([7.5, 22.5, 5])(cylinder(r=2, h=15))
    post4 = translate([22.5, 22.5, 5])(cylinder(r=2, h=15))
    
    # Top platform
    top = translate([0, 0, 20])(cube([30, 30, 3]))
    
    # Holes in base
    hole1 = translate([15, 15, -1])(cylinder(r=3, h=7))
    hole2 = translate([15, 7.5, -1])(cylinder(r=1, h=7))
    hole3 = translate([15, 22.5, -1])(cylinder(r=1, h=7))
    
    # Assemble the final object
    final_object = (base + post1 + post2 + post3 + post4 + top 
                   - hole1 - hole2 - hole3)
    
    print("Viewing complex object...")
    view3d(final_object, width=800, height=600)
    
    return final_object

def using_solidviewer_class():
    """Demonstrate using the SolidViewer class directly."""
    print("Using SolidViewer class...")
    
    # Create a viewer instance (better for multiple objects)
    viewer = SolidViewer()
    
    # Create multiple variations of an object
    for i in range(3):
        for j in range(3):
            # Create a rotated cube at different positions
            obj = translate([i * 20, j * 20, 0])(
                rotate([0, 0, (i + j) * 30])(
                    cube([8, 8, 8])
                )
            )
            
            print(f"Viewing object at position ({i}, {j})...")
            viewer.view(obj, width=400, height=300)

def save_stl_example():
    """Demonstrate saving objects as STL files."""
    print("Creating and saving STL files...")
    
    viewer = SolidViewer()
    
    # Create some objects
    objects = [
        ("cube", cube([10, 10, 10])),
        ("sphere", sphere(6)),
        ("cylinder", cylinder(r=5, h=12)),
    ]
    
    for name, obj in objects:
        filename = f"example_{name}.stl"
        print(f"Saving {name} as {filename}...")
        
        try:
            saved_path = viewer.save_stl(obj, filename, overwrite=True)
            print(f"Successfully saved to: {saved_path}")
        except Exception as e:
            print(f"Error saving {name}: {e}")

if __name__ == "__main__":
    print("SolidView Examples")
    print("=" * 50)
    
    try:
        # Run basic examples
        basic_shapes()
        
        # Create and view a complex object
        complex_obj = complex_object()
        
        # Demonstrate the SolidViewer class
        using_solidviewer_class()
        
        # Save examples as STL
        save_stl_example()
        
        print("\nAll examples completed successfully!")
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Make sure to install: pip install solidpython2 jupyterscad")
    except Exception as e:
        print(f"Error running examples: {e}")