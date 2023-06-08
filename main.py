import bpy
import random
 
# mesh arrays
verts = []
faces = []
 
# mesh variables
numX = 20
numY = 20
 
# wave variables
amp = 3
scale = 2


def apply_modifiers(obj):
    ctx = bpy.context.copy()
    ctx['object'] = obj
    for _, m in enumerate(obj.modifiers):
        try:
            ctx['modifier'] = m
            bpy.ops.object.modifier_apply(ctx, modifier=m.name)
        except RuntimeError:
            print(f"Error applying {m.name} to {obj.name}, removing it instead.")
            obj.modifiers.remove(m)

    for m in obj.modifiers:
        obj.modifiers.remove(m)
        
        

def generate_terrain():
    #fill verts array
    for i in range (0, numX):
        for j in range(0,numY):
     
            x = scale * i
            y = scale * j
            #z = (i*random.random())*amp  
            z = (random.random())*amp
     
            vert = (x,y,z) 
            verts.append(vert)
     
    #fill faces array
    count = 0
    for i in range (0, numY *(numX-1)):
        if count < numY-1:
            A = i
            B = i+1
            C = (i+numY)+1
            D = (i+numY)
     
            face = (A,B,C,D)
            faces.append(face)
            count = count + 1
        else:
            count = 0
     
    #create mesh and object
    mymesh   = bpy.data.meshes.new("TerrainSurface")
    myobject = bpy.data.objects.new("TerrainSurface",mymesh)
     
    #set mesh location
    myobject.location = bpy.context.scene.cursor.location
    bpy.context.collection.objects.link(myobject)
     
    #create mesh from python data
    mymesh.from_pydata(verts,[],faces)
    mymesh.update(calc_edges=True)
     
    # Create the modifier
    modifier = myobject.modifiers.new("subd", type='SUBSURF')
    modifier.levels = 4

    # Remove the modifier
    apply_modifiers(myobject)
        
    return myobject
 



def generate_curve():
    import numpy as np
    from scipy.interpolate import splprep, splev

    # Generate random points on a 10 by 10 surface
    num_points = 10  # Adjust this value as needed
    surface_size = 40

    x = np.random.uniform(0, surface_size, num_points)
    y = np.random.uniform(0, surface_size, num_points)

    # Fit a polynomial spline to the points
    tck, u = splprep([x, y], k=3, s=0)

    # Evaluate the spline to get smooth curve points
    u_new = np.linspace(0, 1, 100)  # Adjust the number of points on the curve as needed
    x_smooth, y_smooth = splev(u_new, tck)

    # Create a new curve object
    curve_data = bpy.data.curves.new('CurveObject', type='CURVE')
    curve_data.dimensions = '2D'

    # Create a new spline and set its points
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(x_smooth)-1)
    for i, (x, y) in enumerate(zip(x_smooth, y_smooth)):
        spline.points[i].co = (x, y, 10, 1)

    # Create a new object and link the curve to it
    curve_obj = bpy.data.objects.new('CurveObject', curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH', keep_original=False)
     
    # Create the modifier
    #modifier = curve_obj.modifiers.new("subd", type='SUBSURF')
    #modifier.levels = 10
    #apply_modifiers(curve_obj)

    # Set the object as the active object and select it
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    
    return curve_obj


 
def project_curve_on_surface(curve_obj_name, terrain_obj_name):
    # Assuming you have already created the target surface object
    curve_obj = bpy.data.objects[ curve_obj_name ]
    target_obj = bpy.data.objects[ terrain_obj_name ]

    # Add the Shrinkwrap modifier to the curve object
    modifier = curve_obj.modifiers.new(name='Shrinkwrap', type='SHRINKWRAP')
    modifier.target = target_obj
    modifier.wrap_mode = 'ON_SURFACE'
    modifier.use_project_z = True
    modifier.use_negative_direction = True

    # Apply the Shrinkwrap modifier
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.modifier_apply(modifier='Shrinkwrap')


def clean_the_scene(): 
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    # Delete selected objects
    bpy.ops.object.delete() 
 




def main():
    clean_the_scene()

    generate_terrain()

    generate_curve()

    #project_curve_on_surface('CurveObject', 'TerrainSurface')

if __name__ == "__main__":
    main()
