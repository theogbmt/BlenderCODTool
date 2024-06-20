import bpy
import os
from . import import_xmodel  # Assuming import_xmodel is in the same package

# Operator for importing XModel or FBX
class Import_XModel_FBX(bpy.types.Operator):
    bl_idname = "wm.import_xmodel_fbx"
    bl_label = "Import XModel or FBX"
    bl_description = "Import an XModel or FBX file"
    bl_options = {'INTERNAL'}
    
    auto_import: bpy.props.BoolProperty(
        name="Auto Import",
        default=True,
        description="If enabled, automatically import the file"
    )

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.auto_import:
            if self.filepath.lower().endswith('.xmodel_bin') or self.filepath.lower().endswith('.xmodel_export'):
                import_xmodel.load(self, context, self.filepath, use_image_search=True)
            elif self.filepath.lower().endswith('.fbx'):
                self.load_fbx_file(self.filepath)
            else:
                print("Unsupported file format")
        else:
            print(f"Prompt to import file: {self.filepath}")
        return {'FINISHED'}

    def load_fbx_file(self, filepath):
        # Replace this with your actual FBX import logic
        print(f"Importing FBX file: {os.path.basename(filepath)}")
        # Example: bpy.ops.import_scene.fbx("EXEC_DEFAULT", filepath=filepath)

# File Handler for both FBX and XModel
class WM_FH_drag_and_drop_files(bpy.types.FileHandler):
    bl_idname = "WM_FH_drag_and_drop_files"
    bl_label = "Import Files"
    bl_file_extensions = {".fbx", ".xmodel_bin", ".xmodel_export"}
    bl_import_operator = "wm.import_xmodel_fbx"

    @classmethod
    def poll_drop(cls, context):
        if context.space_data.type == "VIEW_3D":
            return True

# Custom Tools Panel
class OBJECT_PT_custom_tools_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_custom_tools_panel"
    bl_label = "Custom Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        
        # Auto Import Checkbox for both XModel and FBX
        addon_prefs = context.preferences.addons[__name__].preferences
        row = layout.row()
        row.prop(addon_prefs, "auto_import", text="Auto Import")
        
        # Import Button for XModel and FBX
        row = layout.row()
        row.operator("wm.import_xmodel_fbx", text="Import XModel/FBX")

# Registration and Entry Point
def register():
    bpy.utils.register_class(Import_XModel_FBX)
    bpy.utils.register_class(WM_FH_drag_and_drop_files)
    bpy.utils.register_class(OBJECT_PT_custom_tools_panel)

def unregister():
    bpy.utils.unregister_class(Import_XModel_FBX)
    bpy.utils.unregister_class(WM_FH_drag_and_drop_files)
    bpy.utils.unregister_class(OBJECT_PT_custom_tools_panel)
