#XMODEL DRAG N DROP SUPPORT ADDED
import bpy
import time
from . import import_xmodel  # Adjust this import based on your actual module structure

class Operator_Import_XModel(bpy.types.Operator):
    bl_idname = "wm.import_xmodel"
    bl_label = "Import XModel"
    bl_description = "Import XModel file"
    bl_options = {'INTERNAL'}

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        description="Path to XModel file"
    )

    def execute(self, context):
        start_time = time.process_time()

        # Call the import function from import_xmodel module with hardcoded default values
        result = import_xmodel.load(
            self, context,
            filepath=self.filepath,
            global_scale=1.0,
            apply_unit_scale=False,
            use_single_mesh=True,
            use_dup_tris=True,
            use_custom_normals=True,
            use_vertex_colors=True,
            use_armature=True,
            use_parents=True,
            attach_model=False,
            merge_skeleton=False,
            use_image_search=True
        )

        if not result:
            self.report({'INFO'}, "Import finished in %.4f sec." % (time.process_time() - start_time))
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Automatically execute without showing the file select window
        return self.execute(context)

class WM_FH_drag_and_drop_xmodel(bpy.types.FileHandler):
    bl_idname = "WM_FH_drag_and_drop_xmodel"
    bl_label = "Import XModel"
    bl_import_operator = "wm.import_xmodel"
    bl_file_extensions = ".xmodel_bin"

    @classmethod
    def poll_drop(cls, context):
        if context.space_data.type == "VIEW_3D":
            print("detected")
            return True
        print("not detected")
        return False

class Import_FBX(bpy.types.Operator):
    bl_idname = "wm.import_fbx"
    bl_label = "Import FBX"
    bl_description = "Install Addon"
    bl_options = {'INTERNAL'}
    
    auto_import: bpy.props.BoolProperty(
        name="Auto Import",
        default=True,
        description="If enabled, automatically import the FBX file"
    )

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.auto_import:
            bpy.ops.import_scene.fbx("EXEC_DEFAULT", filepath=self.filepath)
        else:
            bpy.ops.import_scene.fbx("INVOKE_DEFAULT", filepath=self.filepath)
        return {'FINISHED'}

class WM_FH_drag_and_drop_fbx(bpy.types.FileHandler):
    bl_idname = "WM_FH_drag_and_drop_fbx"
    bl_label = "Import FBX"
    bl_import_operator = "wm.import_fbx"
    bl_file_extensions = ".fbx"

    @classmethod
    def poll_drop(cls, context):
        if context.space_data.type == "VIEW_3D":
            print("detected")
            return True
        print("detected")
        return False

def register():
    bpy.utils.register_class(Operator_Import_XModel)
    bpy.utils.register_class(WM_FH_drag_and_drop_xmodel)
    bpy.utils.register_class(Import_FBX)
    bpy.utils.register_class(WM_FH_drag_and_drop_fbx)

def unregister():
    bpy.utils.unregister_class(Operator_Import_XModel)
    bpy.utils.unregister_class(WM_FH_drag_and_drop_xmodel)
    bpy.utils.unregister_class(Import_FBX)
    bpy.utils.unregister_class(WM_FH_drag_and_drop_fbx)

print( '''\n____  __    ____  __ _  ____  ____  ____     ___  __  ____    ____  __    __   __    ____  
(  _ \(  )  (  __)(  ( \(    \(  __)(  _ \   / __)/  \(    \  (_  _)/  \  /  \ (  )  / ___) 
 ) _ (/ (_/\ ) _) /    / ) D ( ) _)  )   /  ( (__(  O )) D (    )( (  O )(  O )/ (_/\\___ \ 
(____/\____/(____)\_)__)(____/(____)(__\_)   \___)\__/(____/   (__) \__/  \__/ \____/(____/ )\n\nBlender COD Version 0.9 Loaded\n\nSpecial thanks to Valy Arhal and Rex for making this more streamlined\n''' )
