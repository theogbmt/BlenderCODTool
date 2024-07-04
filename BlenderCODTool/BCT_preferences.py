from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty, FloatProperty

from .BCT_utilities import submenu_reloader_register, submenu_reloader_unregister

class BlenderCoD_Preferences(AddonPreferences):
    bl_idname = __package__

    def update_submenu_mode_lambda(self, context):
        try:
            submenu_reloader_unregister()
        except:
            try:
                submenu_reloader_register()
            except:
                pass

    def update_scale_length(self, context):
        unit_map = {
            'CENTI':    0.01,
            'MILLI':    0.001,
            'METER':    1.0,
            'KILO':     1000.0,
            'INCH':     0.0254,
            'FOOT':     0.3048,
            'YARD':     0.9144,
            'MILE':     1609.343994,
        }

        if self.unit_enum in unit_map:
            self.scale_length = unit_map[self.unit_enum]

    use_submenu: BoolProperty(
        name="Group Import/Export Buttons",
        default=False,
        update=update_submenu_mode_lambda
    )

    unit_enum: EnumProperty(
        items=(('CENTI', "Centimeters", ""),
               ('MILLI', "Millimeters", ""),
               ('METER', "Meters", ""),
               ('KILO', "Kilometers", ""),
               ('INCH', "Inches", ""),
               ('FOOT', "Feet", ""),
               ('YARD', "Yards", ""),
               ('MILE', "Miles", ""),
               ('CUSTOM', "Custom", ""),
               ),
        name="Default Unit",
        description="The default unit to interpret one Blender Unit as when "
                    "no units are specified in the scene presets",
        default='INCH',
        update=update_scale_length
    )

    scale_length: FloatProperty(
        name="Unit Scale",
        description="Scale factor to use, follows the same conventions as "
                    "Blender's unit scale in the scene properties\n"
                    "(Is the conversion factor to convert one Blender unit to "
                    "one meter)",
        soft_min=0.001,
        soft_max=100.0,
        min=0.00001,
        max=100000.0,
        precision=6,
        step=1,
        default=1.0
    )

    auto_import: BoolProperty(
        name="Auto Import",
        default=True,
        description="Automatically import files when dropped into Blender"
    )

    def draw(self, context):
        layout = self.layout

        # Submenu and Scale Options
        row = layout.row()
        row.prop(self, "use_submenu")
        col = row.column(align=True)
        col.label(text="Units:")
        sub = col.split(align=True)
        sub.prop(self, "unit_enum", text="")
        sub = col.split(align=True)
        sub.enabled = self.unit_enum == 'CUSTOM'
        sub.prop(self, "scale_length")

        # Auto Import Checkbox
        layout.prop(self, "auto_import", text="Auto Import")

        # Import Button
        layout.operator("object.import_fbx_button", text="Import FBX")

    def register():
        bpy.utils.register_class(BlenderCoD_Preferences)

    def unregister():
        bpy.utils.unregister_class(BlenderCoD_Preferences)

    if __name__ == "__main__":
        register()
