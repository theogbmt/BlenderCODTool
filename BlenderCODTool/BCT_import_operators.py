import time
import os

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import (BoolProperty, IntProperty, FloatProperty,
                       StringProperty, EnumProperty, CollectionProperty)

class COD_MT_import_xmodel(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xmodel"
    bl_label = "Import XModel"
    bl_description = "Import a CoD XMODEL_EXPORT / XMODEL_BIN File"
    bl_options = {'PRESET'}

    filename_ext = ".XMODEL_EXPORT;.XMODEL_BIN"
    filter_glob: StringProperty(
        default="*.XMODEL_EXPORT;*.XMODEL_BIN",
        options={'HIDDEN'}
    ) #type:ignore

    ui_tab: EnumProperty(
        items=(('MAIN', "Main", "Main basic settings"),
               ('ARMATURE', "Armature", "Armature-related settings"),
               ),
        name="ui_tab",
        description="Import options categories",
        default='MAIN'
    ) #type:ignore

    global_scale: FloatProperty(
        name="Scale",
        min=0.001, max=1000.0,
        default=1.0,
    ) #type:ignore

    apply_unit_scale: BoolProperty(
        name="Apply Unit",
        description="Scale all data according to current Blender size,"
                    " to match CoD units",
        default=True,
    ) #type:ignore

    use_single_mesh: BoolProperty(
        name="Combine Meshes",
        description="Combine all meshes in the file into a single object",  # nopep8
        default=True
    ) #type:ignore

    use_dup_tris: BoolProperty(
        name="Import Duplicate Tris",
        description=("Import tris that reuse the same vertices as another tri "
                     "(otherwise they are discarded)"),
        default=True
    ) #type:ignore

    use_custom_normals: BoolProperty(
        name="Import Normals",
        description=("Import custom normals, if available "
                     "(otherwise Blender will recompute them)"),
        default=True
    ) #type:ignore

    use_vertex_colors: BoolProperty(
        name="Import Vertex Colors",
        default=True
    ) #type:ignore

    use_armature: BoolProperty(
        name="Import Armature",
        description="Import the skeleton",
        default=True
    ) #type:ignore

    use_parents: BoolProperty(
        name="Import Relationships",
        description="Import the parent / child bone relationships",
        default=True
    ) #type:ignore

    """
    force_connect_children : BoolProperty(
        name="Force Connect Children",
        description=("Force connection of children bones to their parent, "
                     "even if their computed head/tail "
                     "positions do not match"),
        default=False,
    )
    """  # nopep8

    attach_model: BoolProperty(
        name="Attach Model",
        description="Attach head to body, gun to hands, etc.",
        default=False
    ) #type:ignore

    merge_skeleton: BoolProperty(
        name="Merge Skeletons",
        description="Merge imported skeleton with the selected skeleton",
        default=False
    ) #type:ignore

    use_image_search: BoolProperty(
        name="Image Search",
        description=("Search subdirs for any associated images "
                     "(Warning, may be slow)"),
        default=True
    ) #type:ignore

    def execute(self, context):
        from . import import_xmodel
        start_time = time.process_time()

        keywords = self.as_keywords(ignore=("filter_glob",
                                            "check_existing",
                                            "ui_tab"))

        result = import_xmodel.load(self, context, **keywords)

        if not result:
            self.report({'INFO'}, "Import finished in %.4f sec." %
                        (time.process_time() - start_time))
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return (context.scene is not None)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'ui_tab', expand=True)
        if self.ui_tab == 'MAIN':
            # Orientation (Possibly)
            # Axis Options (Possibly)

            row = layout.row(align=True)
            row.prop(self, "global_scale")
            sub = row.row(align=True)
            sub.prop(self, "apply_unit_scale", text="")

            layout.prop(self, 'use_single_mesh')

            layout.prop(self, 'use_custom_normals')
            layout.prop(self, 'use_vertex_colors')
            layout.prop(self, 'use_dup_tris')
            layout.prop(self, 'use_image_search')
        elif self.ui_tab == 'ARMATURE':
            layout.prop(self, 'use_armature')
            col = layout.column()
            col.enabled = self.use_armature
            col.prop(self, 'use_parents')

            # Possibly support force_connect_children?
            # sub = col.split()
            # sub.enabled = self.use_parents
            # sub.prop(self, 'force_connect_children')
            col.prop(self, 'attach_model')
            sub = col.split()
            sub.enabled = self.attach_model
            sub.prop(self, 'merge_skeleton')

class COD_MT_import_xanim(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xanim"
    bl_label = "Import XAnim"
    bl_description = "Import a CoD XANIM_EXPORT / XANIM_BIN File"
    bl_options = {'PRESET'}

    filename_ext = ".XANIM_EXPORT;.NT_EXPORT;.XANIM_BIN"
    filter_glob: StringProperty(
        default="*.XANIM_EXPORT;*.NT_EXPORT;*.XANIM_BIN",
        options={'HIDDEN'}
    ) #type:ignore

    files: CollectionProperty(type=bpy.types.PropertyGroup) #type:ignore

    global_scale: FloatProperty(
        name="Scale",
        min=0.001, max=1000.0,
        default=1.0,
    ) #type:ignore

    apply_unit_scale: BoolProperty(
        name="Apply Unit",
        description="Scale all data according to current Blender size,"
                    " to match CoD units",
        default=True,
    ) #type:ignore

    use_actions: BoolProperty(
        name="Import as Action(s)",
        description=("Import each animation as a separate action "
                     "instead of appending to the current action"),
        default=True
    ) #type:ignore

    use_actions_skip_existing: BoolProperty(
        name="Skip Existing Actions",
        description="Skip animations that already have existing actions",
        default=False
    ) #type:ignore

    use_notetracks: BoolProperty(
        name="Import Notetracks",
        description=("Import notes to scene timeline markers "
                     "(or action pose markers if 'Import as Action' is enabled)"),  # nopep8
        default=True
    ) #type:ignore

    use_notetrack_file: BoolProperty(
        name="Import NT_EXPORT File",
        description=("Automatically import the matching NT_EXPORT file "
                     "(if present) for each XANIM_EXPORT"),
        default=True
    ) #type:ignore

    fps_scale_type: EnumProperty(
        name="Scale FPS",
        description="Automatically convert all imported animation(s) to the specified framerate",   # nopep8
        items=(('DISABLED', "Disabled", "No framerate adjustments are applied"),   # nopep8
               ('SCENE', "Scene", "Use the scene's framerate"),
               ('CUSTOM', "Custom", "Use custom framerate")
               ),
        default='DISABLED',
    ) #type:ignore

    fps_scale_target_fps: FloatProperty(
        name="Target FPS",
        description=("Custom framerate that all imported anims "
                     "will be adjusted to use"),
        default=30,
        min=1,
        max=120
    ) #type:ignore

    update_scene_fps: BoolProperty(
        name="Update Scene FPS",
        description=("Set the scene framerate to match the framerate "
                     "found in the first imported animation"),
        default=False
    ) #type:ignore

    anim_offset: FloatProperty(
        name="Animation Offset",
        description="Offset to apply to animation during import, in frames",
        default=1.0,
    ) #type:ignore

    def execute(self, context):
        from . import import_xanim
        start_time = time.process_time()

        ignored_properties = ("filter_glob", "files", "apply_unit_scale")
        result = import_xanim.load(
            self,
            context,
            self.apply_unit_scale,
            **self.as_keywords(ignore=ignored_properties))

        if not result:
            self.report({'INFO'}, "Import finished in %.4f sec." %
                        (time.process_time() - start_time))
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return (context.scene is not None)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "global_scale")
        sub = row.row(align=True)
        sub.prop(self, "apply_unit_scale", text="")

        layout.prop(self, 'use_actions')
        sub = layout.split()
        sub.enabled = self.use_actions
        sub.prop(self, 'use_actions_skip_existing')
        layout.prop(self, 'use_notetracks')
        sub = layout.split()
        sub.enabled = self.use_notetracks
        sub.prop(self, 'use_notetrack_file')

        sub = layout.box()
        split = sub.split(factor=0.55)
        split.label(text="Scale FPS:")
        split.prop(self, 'fps_scale_type', text="")
        if self.fps_scale_type == 'DISABLED':
            sub.prop(self, "update_scene_fps")
        elif self.fps_scale_type == 'SCENE':
            sub.label(text="Target Framerate: %.2f" % context.scene.render.fps)
        elif self.fps_scale_type == 'CUSTOM':
            sub.prop(self, 'fps_scale_target_fps')
        layout.prop(self, 'anim_offset')

class COD_MT_export_xmodel(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.xmodel"
    bl_label = 'Export XModel'
    bl_description = "Export a CoD XMODEL_EXPORT / XMODEL_BIN File"
    bl_options = {'PRESET'}

    filename_ext = ".XMODEL_EXPORT"
    filter_glob: StringProperty(
        default="*.XMODEL_EXPORT;*.XMODEL_BIN", options={'HIDDEN'}) #type:ignore

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    # Used to map target_format values to actual file extensions
    format_ext_map = {
        'XMODEL_EXPORT': '.XMODEL_EXPORT',
        'XMODEL_BIN': '.XMODEL_BIN'
    }

    target_format: EnumProperty(
        name="Format",
        description="The target format to export to",
        items=(('XMODEL_EXPORT', "XMODEL_EXPORT",
                "Raw text format used from CoD1-CoD:BO"),
               ('XMODEL_BIN', "XMODEL_BIN",
                "Binary model format used by CoD:BO3")),
        default='XMODEL_EXPORT'
    ) #type:ignore

    version: EnumProperty(
        name="Version",
        description="XMODEL_EXPORT format version for export",
        items=(('5', "Version 5", "vCoD, CoD:UO"),
               ('6', "Version 6", "CoD2, CoD4, CoD:WaW, CoD:BO"),
               ('7', "Version 7", "CoD:BO3")),
        default='6'
    ) #type:ignore

    use_selection: BoolProperty(
        name="Selection only",
        description=("Export selected meshes only "
                     "(object or weight paint mode)"),
        default=False
    ) #type:ignore

    global_scale: FloatProperty(
        name="Scale",
        min=0.001, max=1000.0,
        default=1.0,
    ) #type:ignore

    apply_unit_scale: BoolProperty(
        name="Apply Unit",
        description="Scale all data according to current Blender size,"
                    " to match CoD units",
        default=True,
    ) #type:ignore

    use_vertex_colors: BoolProperty(
        name="Vertex Colors",
        description=("Export vertex colors "
                     "(if disabled, white color will be used)"),
        default=True
    ) #type:ignore

    #  White is 1 (opaque), black 0 (invisible)
    use_vertex_colors_alpha: BoolProperty(
        name="Calculate Alpha",
        description=("Automatically calculate alpha channel for vertex colors "
                     "by averaging the RGB color values together "
                     "(if disabled, 1.0 is used)"),
        default=False
    ) #type:ignore

    use_vertex_colors_alpha_mode: EnumProperty(
        name="Vertex Alpha Source Layer",
        description="The target vertex color layer to use for calculating the alpha values",  # nopep8
        items=(('PRIMARY', "Active Layer",
                "Use the active vertex color layer to calculate alpha"),
               ('SECONDARY', "Secondary Layer",
                ("Use the secondary (first inactive) vertex color layer to calculate alpha "  # nopep8
                 "(If only one layer is present, the active layer is used)")),
               ),
        default='PRIMARY'
    ) #type:ignore

    use_vertex_cleanup: BoolProperty(
        name="Clean Up Vertices",
        description=("Try this if you have problems converting to xmodel. "
                     "Skips vertices which aren't used by any face "
                     "and updates references."),
        default=False
    ) #type:ignore

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply all mesh modifiers (except Armature)",
        default=False
    ) #type:ignore

    modifier_quality: EnumProperty(
        name="Modifier Quality",
        description="The quality at which to apply mesh modifiers",
        items=(('PREVIEW', "Preview", ""),
               ('RENDER', "Render", ""),
               ),
        default='PREVIEW'
    ) #type:ignore

    use_armature: BoolProperty(
        name="Armature",
        description=("Export bones "
                     "(if disabled, only a 'tag_origin' bone will be written)"),  # nopep8
        default=True
    ) #type:ignore

    """
    use_armature_pose : BoolProperty(
        name="Pose animation to models",
        description=("Export meshes with Armature modifier applied "
                     "as a series of XMODEL_EXPORT files"),
        default=False
    )

    frame_start : IntProperty(
        name="Start",
        description="First frame to export",
        default=1,
        min=0
    )

    frame_end : IntProperty(
        name="End",
        description="Last frame to export",
        default=250,
        min=0
    )
    """

    use_weight_min: BoolProperty(
        name="Minimum Bone Weight",
        description=("Try this if you get 'too small weight' "
                     "errors when converting"),
        default=False,
    ) #type:ignore

    use_weight_min_threshold: FloatProperty(
        name="Threshold",
        description="Smallest allowed weight (minimum value)",
        default=0.010097,
        min=0.0,
        max=1.0,
        precision=6
    ) #type:ignore

    def execute(self, context):
        from . import export_xmodel
        start_time = time.process_time()

        ignore = ("filter_glob", "check_existing")
        result = export_xmodel.save(self, context,
                                    **self.as_keywords(ignore=ignore))

        if not result:
            self.report({'INFO'}, "Export finished in %.4f sec." %
                        (time.process_time() - start_time))
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return (context.scene is not None)

    def check(self, context):
        '''
        This is a modified version of the ExportHelper check() method
        This one provides automatic checking for the file extension
         based on what 'target_format' is (through 'format_ext_map')
        '''
        import os
        from bpy_extras.io_utils import _check_axis_conversion
        change_ext = False
        change_axis = _check_axis_conversion(self)

        check_extension = self.check_extension

        if check_extension is not None:
            filepath = self.filepath
            if os.path.basename(filepath):
                # If the current extension is one of the valid extensions
                #  (as defined by this class), strip the extension, and ensure
                #  that it has the correct one
                # (needed when switching extensions)
                base, ext = os.path.splitext(filepath)
                if ext[1:] in self.format_ext_map:
                    filepath = base
                target_ext = self.format_ext_map[self.target_format]
                filepath = bpy.path.ensure_ext(filepath,
                                               target_ext
                                               if check_extension
                                               else "")

                if filepath != self.filepath:
                    self.filepath = filepath
                    change_ext = True

        return (change_ext or change_axis)

    # Extend ExportHelper invoke function to support dynamic default values
    def invoke(self, context, event):

        # self.use_frame_start = context.scene.frame_start
        self.use_frame_start = context.scene.frame_current

        # self.use_frame_end = context.scene.frame_end
        self.use_frame_end = context.scene.frame_current

        return super().invoke(context, event)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'target_format', expand=True)
        layout.prop(self, 'version')

        # Calculate number of selected mesh objects
        if context.mode in ('OBJECT', 'PAINT_WEIGHT'):
            objects = bpy.data.objects
            meshes_selected = len(
                [m for m in objects if m.type == 'MESH' and m.select_get()])
        else:
            meshes_selected = 0

        layout.prop(self, 'use_selection',
                    text="Selected Only (%d meshes)" % meshes_selected)

        row = layout.row(align=True)
        row.prop(self, "global_scale")
        sub = row.row(align=True)
        sub.prop(self, "apply_unit_scale", text="")

        # Axis?

        sub = layout.split(factor=0.5)
        sub.prop(self, 'apply_modifiers')
        sub = sub.row()
        sub.enabled = self.apply_modifiers
        sub.prop(self, 'modifier_quality', expand=True)

        # layout.prop(self, 'custom_normals')

        if int(self.version) >= 6:
            row = layout.row()
            row.prop(self, 'use_vertex_colors')
            sub = row.split()
            sub.enabled = self.use_vertex_colors
            sub.prop(self, 'use_vertex_colors_alpha')
            sub = layout.split()
            sub.enabled = (self.use_vertex_colors and
                           self.use_vertex_colors_alpha)
            sub = sub.split(factor=0.5)
            sub.label(text="Vertex Alpha Layer")
            sub.prop(self, 'use_vertex_colors_alpha_mode', text="")

        layout.prop(self, 'use_vertex_cleanup')

        layout.prop(self, 'use_armature')
        box = layout.box()
        box.enabled = self.use_armature
        sub = box.column(align=True)
        sub.prop(self, 'use_weight_min')
        sub = box.split(align=True)
        sub.active = self.use_weight_min
        sub.prop(self, 'use_weight_min_threshold')

class COD_MT_export_xanim(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.xanim"
    bl_label = 'Export XAnim'
    bl_description = "Export a CoD XANIM_EXPORT / XANIM_BIN File"
    bl_options = {'PRESET'}

    filename_ext = ".XANIM_EXPORT"
    filter_glob: StringProperty(
        default="*.XANIM_EXPORT;*.XANIM_BIN", options={'HIDDEN'}) #type:ignore

    # Used to map target_format values to actual file extensions
    format_ext_map = {
        'XANIM_EXPORT': '.XANIM_EXPORT',
        'XANIM_BIN': '.XANIM_BIN'
    }

    target_format: EnumProperty(
        name="Format",
        description="The target format to export to",
        items=(('XANIM_EXPORT', "XANIM_EXPORT",
                "Raw text format used from CoD1-CoD:BO"),
               ('XANIM_BIN', "XANIM_BIN",
                "Binary animation format used by CoD:BO3")),
        default='XANIM_EXPORT'
    ) #type:ignore

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected bones only (pose mode)",
        default=False
    ) #type:ignore

    global_scale: FloatProperty(
        name="Scale",
        min=0.001, max=1000.0,
        default=1.0,
    ) #type:ignore

    apply_unit_scale: BoolProperty(
        name="Apply Unit",
        description="Scale all data according to current Blender size,"
                    " to match CoD units",
        default=True,
    ) #type:ignore

    use_all_actions: BoolProperty(
        name="Export All Actions",
        description="Export *all* actions rather than just the active one",
        default=False
    ) #type:ignore

    filename_format: StringProperty(
        name="Format",
        description=("The format string for the filenames when exporting multiple actions\n"  # nopep8
                     "%action, %s - The action name\n"
                     "%number, %d - The action number\n"
                     "%base,   %b - The base filename (at the top of the export window)\n"  # nopep8
                     ""),
        default="%action"
    ) #type:ignore

    use_notetracks: BoolProperty(
        name="Notetracks",
        description="Export notetracks",
        default=True
    ) #type:ignore

    use_notetrack_mode: EnumProperty(
        name="Notetrack Mode",
        description="Notetrack format to use. Always set 'CoD 7' for Black Ops, even if not using notetrack!",   # nopep8
        items=(('SCENE', "Scene",
                "Separate NT_EXPORT notetrack file for 'World at War'"),
               ('ACTION', "Action",
                "Separate NT_EXPORT notetrack file for 'Black Ops'")),
        default='ACTION'
    ) #type:ignore

    use_notetrack_format: EnumProperty(
        name="Notetrack format",
        description=("Notetrack format to use. "
                     "Always set 'CoD 7' for Black Ops, "
                     "even if not using notetrack!"),
        items=(('5', "CoD 5",
                "Separate NT_EXPORT notetrack file for 'World at War'"),
               ('7', "CoD 7",
                "Separate NT_EXPORT notetrack file for 'Black Ops'"),
               ('1', "all other",
                "Inline notetrack data for all CoD versions except WaW and BO")
               ),
        default='1'
    ) #type:ignore

    use_notetrack_file: BoolProperty(
        name="Write NT_EXPORT",
        description=("Create an NT_EXPORT file for "
                     "the exported XANIM_EXPORT file(s)"),
        default=False
    ) #type:ignore

    use_frame_range_mode: EnumProperty(
        name="Frame Range Mode",
        description="Decides what to use for the frame range",
        items=(('SCENE', "Scene", "Use the scene's frame range"),
               ('ACTION', "Action", "Use the frame range from each action"),
               ('CUSTOM', "Custom", "Use a user-defined frame range")),
        default='ACTION'
    ) #type:ignore

    frame_start: IntProperty(
        name="Start",
        description="First frame to export",
        min=0,
        default=1
    ) #type:ignore

    frame_end: IntProperty(
        name="End",
        description="Last frame to export",
        min=0,
        default=250
    ) #type:ignore

    use_custom_framerate: BoolProperty(
        name="Custom Framerate",
        description=("Force all written files to use a user defined "
                     "custom framerate rather than the scene's framerate"),
        default=False
    ) #type:ignore

    use_framerate: IntProperty(
        name="Framerate",
        description=("Set frames per second for export, "
                     "30 fps is commonly used."),
        default=30,
        min=1,
        max=1000
    ) #type:ignore

    def execute(self, context):
        from . import export_xanim
        start_time = time.process_time()
        result = export_xanim.save(
            self,
            context,
            **self.as_keywords(ignore=("filter_glob", "check_existing")))

        if not result:
            msg = "Export finished in %.4f sec." % (time.process_time() - start_time)
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return (context.scene is not None)

    def check(self, context):
        '''
        This is a modified version of the ExportHelper check() method
        This one provides automatic checking for the file extension
         based on what 'target_format' is (through 'format_ext_map')
        '''
        import os
        from bpy_extras.io_utils import _check_axis_conversion
        change_ext = False
        change_axis = _check_axis_conversion(self)

        check_extension = self.check_extension

        if check_extension is not None:
            filepath = self.filepath
            if os.path.basename(filepath):
                # If the current extension is one of the valid extensions
                #  (as defined by this class), strip the extension, and ensure
                #  that it has the correct one
                # (needed when switching extensions)
                base, ext = os.path.splitext(filepath)
                if ext[1:] in self.format_ext_map:
                    filepath = base
                target_ext = self.format_ext_map[self.target_format]
                filepath = bpy.path.ensure_ext(filepath,
                                               target_ext
                                               if check_extension
                                               else "")

                if filepath != self.filepath:
                    self.filepath = filepath
                    change_ext = True

        return (change_ext or change_axis)

    '''
    # Extend ExportHelper invoke function to support dynamic default values
    def invoke(self, context, event):

        self.use_frame_start = context.scene.frame_start
        self.use_frame_end = context.scene.frame_end
        # self.use_framerate = round(
        #     context.scene.render.fps / context.scene.render.fps_base)

        return super().invoke(context, event)
    '''

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'target_format', expand=True)
        layout.prop(self, 'use_selection')

        row = layout.row(align=True)
        row.prop(self, "global_scale")
        sub = row.row(align=True)
        sub.prop(self, "apply_unit_scale", text="")

        action_count = len(bpy.data.actions)

        sub = layout.split()
        sub.enabled = action_count > 0
        sub.prop(self, 'use_all_actions',
                 text='Export All Actions (%d actions)' % action_count)

        # Filename Options
        if self.use_all_actions and action_count > 0:
            sub = layout.column(align=True)
            sub.label(text="Filename Options:")
            box = sub.box()
            sub = box.column(align=True)

            sub.prop(self, 'filename_format')

            ex_num = action_count - 1
            ex_action = bpy.data.actions[ex_num].name
            ex_base = os.path.splitext(os.path.basename(self.filepath))[0]

            try:
                icon = 'NONE'
                from . import export_xanim
                template = export_xanim.CustomTemplate(self.filename_format)
                example = template.format(ex_action, ex_base, ex_num)
            except Exception as err:
                icon = 'ERROR'
                example = str(err)

            sub.label(text=example, icon=icon)

        # Notetracks
        col = layout.column(align=True)
        sub = col.row()
        sub = sub.split(factor=0.45)
        sub.prop(self, 'use_notetracks', text="Use Notetrack")
        sub.row().prop(self, 'use_notetrack_mode', expand=True)
        sub = col.column()
        sub.enabled = self.use_notetrack_mode != 'NONE'

        sub = sub.split()
        sub.enabled = self.use_notetracks
        sub.prop(self, 'use_notetrack_file')

        # Framerate
        layout.prop(self, 'use_custom_framerate')
        sub = layout.split()
        sub.enabled = self.use_custom_framerate
        sub.prop(self, 'use_framerate')

        # Frame Range
        sub = layout.row()
        sub.label(text="Frame Range:")
        sub.prop(self, 'use_frame_range_mode', text="")

        sub = layout.row(align=True)
        sub.enabled = self.use_frame_range_mode == 'CUSTOM'
        sub.prop(self, 'frame_start')
        sub.prop(self, 'frame_end')
