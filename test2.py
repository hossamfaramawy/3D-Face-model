import bpy
import os
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty
)
from bpy.types import Operator
from keentools_facebuilder.fbloader import FBLoader
from keentools_facebuilder.utils import cameras, manipulate, materials, coords, images
from keentools_facebuilder.utils.attrs import get_obj_collection, safe_delete_collection
from keentools_facebuilder.utils.exif_reader import (update_exif_sizes_message,
copy_exif_parameters_from_camera_to_head)
from keentools_facebuilder.utils.manipulate import check_settings
from keentools_facebuilder.utils.operator_action import (create_blendshapes,
                                    delete_blendshapes,
                                    load_animation_from_csv,
                                    create_example_animation,
                                    reset_blendshape_values,
                                    clear_animation,
                                    export_head_to_fbx,
                                    update_blendshapes,
                                    unhide_head,
                                    reconstruct_by_mesh)

from keentools_facebuilder.config import Config, ErrorType, get_main_settings, get_operator
from keentools_facebuilder.utils import coords
from keentools_facebuilder.utils.focal_length import configure_focal_mode_and_fixes
from keentools_facebuilder.utils.manipulate import push_neutral_head_in_undo_history

class building():
    headnum = 0
    def exec(self):
        #importing the obj
        file_loc = 'C:\\Users\\pc\\Downloads\\dd\\blender\\untitled.obj'
        imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
        obj_object = bpy.context.selected_objects[0]


        #selecting the object
        behindFace = bpy.data.objects["FaceBuilderHead_FaceBuilderHead_mesh"].select_set(True)

        #creation of material
        #bpy.ops.material.new()
        #assign the material to variable
        mat = bpy.data.materials["(null)"]

        #checking the nodes are true
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        #using the nodes to change the value of colors
        nodes["Principled BSDF"].inputs[0].default_value = (0.222, 0.9, 0.8, 1)

        #assigning the object to the material that was created
        #ob = bpy.context.object.data.materials.append(mat)

        #adding the face into the blender
        bpy.ops.keentools_facebuilder.add_head()
        #saving the face into blender
        face = bpy.context.active_object


        #removing the scalp and neck 
        bpy.context.scene.keentools_fb_settings.heads[0].masks[6] = False
        bpy.context.scene.keentools_fb_settings.heads[0].masks[4] = False
        bpy.context.scene.keentools_fb_settings.heads[0].masks[0] = False


         
         
    def execute(self):
            
        filepath='C:\\Users\\pc\\Downloads\\dd\\blender\\GettyImages-1092658864_hero-1024x575.jpg'
        head = FBLoader.load_model(0)
        camera = FBLoader.add_new_camera_with_image(self.headnum,filepath)
        

def get_detected_faces():
    global _DETECTED_FACES
    return _DETECTED_FACES

def _set_detected_faces(faces_info):
    global _DETECTED_FACES
    _DETECTED_FACES = faces_info

def _get_detected_faces_rectangles():
    faces = get_detected_faces()
    rects = []
    for i, face in enumerate(faces):
        x1, y1 = face.xy_min
        x2, y2 = face.xy_max
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        rects.append((x1, y1, x2, y2, i))
    return rects

def init_detected_faces(fb, headnum, camnum):
    settings = get_main_settings()
    head = settings.get_head(headnum)
    camera = head.get_camera(camnum)
    img = camera.np_image()
    fb.set_use_emotions(head.should_use_emotions())
    _set_detected_faces(fb.detect_faces(img))

    return img

def sort_detected_faces():
    faces = get_detected_faces()
    rects = _get_detected_faces_rectangles()
    rects.sort(key=lambda x: x[0])  # order by x1
    _set_detected_faces([faces[x[4]] for x in rects])
    return rects

def _add_pins_to_face(headnum, camnum, rectangle_index):
    fb = FBLoader.get_builder()
    faces = get_detected_faces()

    settings = get_main_settings()
    head = settings.get_head(headnum)
    camera = head.get_camera(camnum)
    kid = camera.get_keyframe()

    fb.set_use_emotions(head.should_use_emotions())
    configure_focal_mode_and_fixes(fb, head)
    result_flag = fb.detect_face_pose(kid, faces[rectangle_index])
    if result_flag:
        fb.remove_pins(kid)
        fb.add_preset_pins(kid)
        print("added")
    else:
        print("failed")

    FBLoader.update_pins_count(headnum, camnum)
    FBLoader.update_all_camera_positions(headnum)
    FBLoader.update_all_camera_focals(headnum)
    FBLoader.fb_redraw(headnum, camnum)

    FBLoader.save_only(headnum)
    history_name = 'Add face auto-pins' if result_flag else 'No auto-pins'
    push_neutral_head_in_undo_history(head, kid, history_name)
    return result_flag

class exec():
    headnum=0
    camnum=0

    def action(self):

        FBLoader.load_model(self.headnum)
        fb = FBLoader.get_builder()

        if not fb.is_face_detector_available():
            print('Face detector is not available')
            return 

        img = init_detected_faces(fb, self.headnum, self.camnum)
        h, w, _ = img.shape
        rects = sort_detected_faces()

        vp = FBLoader.viewport()
        rectangler = vp.rectangler()
        rectangler.clear_rectangles()

        if len(rects) > 1:
            for x1, y1, x2, y2, _ in rects:
                rectangler.add_rectangle(x1, y1, x2, y2, w, h,Config.regular_rectangle_color)
            if invoked:
                op = get_operator(Config.fb_pickmode_idname)
                op('INVOKE_DEFAULT', headnum=self.headnum, camnum=self.camnum)
        elif len(rects) == 1:
            if not _add_pins_to_face(self.headnum, self.camnum,rectangle_index=0):
                print("A face wasn't detected and pinned")
                return  
            else:
                print("A face was detected and pinned")
                return
        #expanding the edges
        bpy.context.scene.keentools_fb_settings.tex_uv_expand_percents = 10

        #creating the texturing
        bpy.ops.keentools_facebuilder.bake_tex(headnum=0)

        bpy.ops.keentools_facebuilder.tex_selector(headnum=0)

        
if __name__=='__main__':
    y= building()
    y.exec() 
    y.execute()
    x = exec()
    x.action()
