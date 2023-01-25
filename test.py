import bpy
import os

#importing the obj
file_loc = 'C:\\Users\\pc\\Desktop\\blender\\untitled.obj'
imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
obj_object = bpy.context.selected_objects[0]


#selecting the object
behindFace = bpy.data.objects["FaceBuilderHead_FaceBuilderHead_mesh"].select_set(True)

#creation of material
mat = bpy.data.materials["(null)"]

#checking the nodes are true
mat.use_nodes = True
nodes = mat.node_tree.nodes

#using the nodes to change the value of colors
nodes["Principled BSDF"].inputs[0].default_value = (0.222, 0.9, 0.8, 1)


#adding the face into the blender
bpy.ops.keentools_facebuilder.add_head()
#saving the face into blender
face = bpy.context.active_object


#removing the scalp and neck 
bpy.context.scene.keentools_fb_settings.heads[0].masks[6] = False
bpy.context.scene.keentools_fb_settings.heads[0].masks[4] = False
bpy.context.scene.keentools_fb_settings.heads[0].masks[0] = False



#directory into variable
directory = os.path.dirname("C:\\Users\\pc\\Desktop\\blender\\")

#making the new obj file that will be saved into
target_file = os.path.join(directory, 'DefaultFace.obj')

#saving the obj into the export file
bpy.ops.export_scene.obj(filepath=target_file)





