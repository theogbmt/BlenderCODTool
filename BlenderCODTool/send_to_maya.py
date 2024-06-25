#added cod_scaling setting
import bpy
import subprocess
import os
import json

# Function to get the path to the maya_settings.json file
def get_settings_file():
    return os.path.join(os.path.dirname(__file__), "maya_settings.json")

# Function to read the Maya path and scaling from maya_settings.json
def read_settings():
    settings_file = get_settings_file()
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            return json.load(file)
    return {"maya_path": "", "scale_value": 1.0}

# Function to write the Maya path and scaling to maya_settings.json
def write_settings(maya_path, scale_value):
    settings_file = get_settings_file()
    with open(settings_file, "w") as file:
        json.dump({"maya_path": maya_path, "scale_value": scale_value}, file)

# Operator to set Maya path
class OBJECT_OT_set_maya_path(bpy.types.Operator):
    bl_idname = "object.set_maya_path"
    bl_label = "Set Maya Path"
    bl_description = "Set the path to the Maya executable"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        write_settings(self.filepath, read_settings()["scale_value"])
        self.report({'INFO'}, "Maya path saved.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Operator to switch to Blender scaling
class OBJECT_OT_switch_to_blender_scaling(bpy.types.Operator):
    bl_idname = "object.switch_to_blender_scaling"
    bl_label = "Switch to Blender Scaling"
    bl_description = "Switch all settings to Blender scaling standards"

    def execute(self, context):
        # Reset scaling to Blender's default (1 Blender Unit = 1 meter)
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = 1.0
        bpy.context.scene.unit_settings.length_unit = 'METERS'
        write_settings(read_settings()["maya_path"], 1.0)  # Update scale value in settings file
        return {'FINISHED'}

# Operator to switch to CoD scaling
class OBJECT_OT_switch_to_cod_scaling(bpy.types.Operator):
    bl_idname = "object.switch_to_cod_scaling"
    bl_label = "Switch to COD Scaling"
    bl_description = "Switch all settings to COD inch/unit scaling standards"

    def execute(self, context):
        # Set unit system to Imperial (inches)
        bpy.context.scene.unit_settings.system = 'IMPERIAL'
        bpy.context.scene.unit_settings.length_unit = 'INCHES'
        bpy.context.scene.unit_settings.scale_length = 1.0 / 39.3701  # Convert 1 meter to inches
        write_settings(read_settings()["maya_path"], 1.0 / 39.3701)  # Update scale value in settings file
        return {'FINISHED'}

# Operator to switch to Maya scaling
class OBJECT_OT_switch_to_maya_scaling(bpy.types.Operator):
    bl_idname = "object.switch_to_maya_scaling"
    bl_label = "Switch to Maya Scaling"
    bl_description = "Switch all settings to Maya scaling standards"

    def execute(self, context):
        # Set scaling to Maya's default (1 Maya Unit = 1 centimeter)
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.context.scene.unit_settings.length_unit = 'CENTIMETERS'
        write_settings(read_settings()["maya_path"], 0.01)  # Update scale value in settings file
        return {'FINISHED'}

# Operator to apply Maya transforms
class OBJECT_OT_apply_maya_transforms(bpy.types.Operator):
    bl_idname = "object.apply_maya_transforms"
    bl_label = "Apply Maya Transforms"
    bl_description = "Sets Z-up orientation and applies Maya scaling"

    def execute(self, context):
        # Set Z-up orientation
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', orient_type='GLOBAL')

        # Apply scaling for Maya (1 unit in Maya = 1 meter in Blender)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.transform_apply(location=False)

        return {'FINISHED'}

# Operator to send selected objects to Maya as FBX
class OBJECT_OT_send_to_maya(bpy.types.Operator):
    bl_idname = "object.send_to_maya"
    bl_label = "Send to Maya"
    bl_description = "Exports and imports the selected objects into Maya"

    def execute(self, context):
        # Export selected objects as FBX
        filepath = bpy.path.abspath("//exported_model.fbx")
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)

        # Read Maya path from the JSON settings file
        maya_settings = read_settings()
        maya_path = maya_settings["maya_path"]

        if not maya_path or not os.path.exists(maya_path):
            self.report({'ERROR'}, "Maya path not found. Please set the path using the 'Set Maya Path' button.")
            return {'CANCELLED'}

        # Launch Maya with command to load FBX plugin and import the exported FBX file
        try:
            # Construct the command to load FBX plugin and import FBX into Maya
            maya_script = '''
                if (!`pluginInfo -q -l "fbxmaya"`) loadPlugin "fbxmaya";
                file -import -type "FBX" -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "fbxImport" "{}";
            '''.format(filepath.replace("\\", "/"))
            subprocess.Popen([maya_path, '-command', maya_script])
        except Exception as e:
            self.report({'ERROR'}, f"Failed to launch Maya: {str(e)}")

        return {'FINISHED'}

    def invoke(self, context, event):
        maya_settings = read_settings()
        maya_path = maya_settings["maya_path"]

        if not maya_path:
            return context.window_manager.invoke_props_dialog(self)

        return self.execute(context)


# Panel in the Item category to display the Maya Tools
class VIEW3D_PT_maya_tools_panel(bpy.types.Panel):
    bl_label = "Maya Tools"
    bl_idname = "VIEW3D_PT_maya_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'COD Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.apply_maya_transforms", text="Apply Maya Transforms")
        layout.operator("object.send_to_maya", text="Send to Maya")
        layout.operator("object.set_maya_path", text="Set Maya Path")


# Panel to display scaling tools
class VIEW3D_PT_scaling_tools_panel(bpy.types.Panel):
    bl_label = "Scaling Tools"
    bl_idname = "VIEW3D_PT_scaling_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'COD Tools'  # Should be under the Maya category

    def draw(self, context):
        layout = self.layout

        layout.separator()
        layout.label(text="Scaling Options:")

        layout.operator("object.switch_to_blender_scaling", text="Switch to Blender Scaling")
        layout.operator("object.switch_to_maya_scaling", text="Switch to Maya Scaling")
        layout.operator("object.switch_to_cod_scaling", text="Switch to COD Scaling")


# Register all classes
def register():
    bpy.utils.register_class(OBJECT_OT_set_maya_path)
    bpy.utils.register_class(OBJECT_OT_apply_maya_transforms)
    bpy.utils.register_class(OBJECT_OT_send_to_maya)
    bpy.utils.register_class(VIEW3D_PT_maya_tools_panel)
    bpy.utils.register_class(OBJECT_OT_switch_to_blender_scaling)
    bpy.utils.register_class(OBJECT_OT_switch_to_maya_scaling)
    bpy.utils.register_class(OBJECT_OT_switch_to_cod_scaling)
    bpy.utils.register_class(VIEW3D_PT_scaling_tools_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_set_maya_path)
    bpy.utils.unregister_class(OBJECT_OT_apply_maya_transforms)
    bpy.utils.unregister_class(OBJECT_OT_send_to_maya)
    bpy.utils.unregister_class(VIEW3D_PT_maya_tools_panel)
    bpy.utils.unregister_class(OBJECT_OT_switch_to_blender_scaling)
    bpy.utils.unregister_class(OBJECT_OT_switch_to_maya_scaling)
    bpy.utils.unregister_class(OBJECT_OT_switch_to_cod_scaling)
    bpy.utils.unregister_class(VIEW3D_PT_scaling_tools_panel)
