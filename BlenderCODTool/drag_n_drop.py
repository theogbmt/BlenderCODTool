import bpy

class WM_FH_drag_and_drop_fbx(bpy.types.FileHandler):
    bl_idname = "WM_FH_drag_and_drop_fbx"
    bl_label = "Import FBX"
    bl_import_operator = "wm.import_fbx"
    bl_file_extensions = ".fbx"

    @classmethod
    def poll_drop(cls, context):
        if context.space_data.type == "VIEW_3D":
            return True

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

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")#type:ignore

    def execute(self, context):
        if self.auto_import:
            bpy.ops.import_scene.fbx("EXEC_DEFAULT", filepath=self.filepath)
        else:
            bpy.ops.import_scene.fbx("INVOKE_DEFAULT", filepath=self.filepath)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(WM_FH_drag_and_drop_fbx)
    bpy.utils.register_class(Import_FBX)

def unregister():
    bpy.utils.unregister_class(WM_FH_drag_and_drop_fbx)
    bpy.utils.unregister_class(Import_FBX)

print( '''\n____  __    ____  __ _  ____  ____  ____     ___  __  ____    ____  __    __   __    ____  
(  _ \(  )  (  __)(  ( \(    \(  __)(  _ \   / __)/  \(    \  (_  _)/  \  /  \ (  )  / ___) 
 ) _ (/ (_/\ ) _) /    / ) D ( ) _)  )   /  ( (__(  O )) D (    )( (  O )(  O )/ (_/\\___ \ 
(____/\____/(____)\_)__)(____/(____)(__\_)   \___)\__/(____/   (__) \__/  \__/ \____/(____/ )\n\nBlender COD Version 0.9 Loaded\n\nSpecial thanks to Valy Arhal and Rex for making this more streamlined\n''' )
