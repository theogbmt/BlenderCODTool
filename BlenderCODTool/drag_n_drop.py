#updated 20:03 08/07/2024
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

class Import_FBX(bpy.types.Operator):
    bl_idname = "wm.import_fbx"
    bl_label = "Import FBX"
    bl_description = "Import FBX file"
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

def draw_menu_import(self, context):
    layout = self.layout
    layout.operator(Operator_Import_XModel.bl_idname, text="Import XModel")
    layout.operator(Import_FBX.bl_idname, text="Import FBX")

def drop_handler(filepath):
    # Determine the file type and call the appropriate import operator
    if filepath.lower().endswith(".xmodel_bin"):
        bpy.ops.wm.import_xmodel(filepath=filepath)
    elif filepath.lower().endswith(".fbx"):
        bpy.ops.wm.import_fbx(filepath=filepath)
    else:
        print("Unsupported file format:", filepath)

def register():
    bpy.utils.register_class(Operator_Import_XModel)
    bpy.utils.register_class(Import_FBX)
    bpy.types.TOPBAR_MT_file_import.append(draw_menu_import)
    bpy.types.WindowManager.fileselect_add(drop_handler)

def unregister():
    bpy.utils.unregister_class(Operator_Import_XModel)
    bpy.utils.unregister_class(Import_FBX)
    bpy.types.TOPBAR_MT_file_import.remove(draw_menu_import)
    bpy.types.WindowManager.fileselect_remove(drop_handler)
