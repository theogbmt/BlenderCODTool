import bpy

from .BCT_submenus import menu_func_import_submenu, menu_func_export_submenu, menu_func_xmodel_import, menu_func_xanim_export, menu_func_xanim_import, menu_func_xmodel_export

def submenu_reloader_register():
    preferences = bpy.context.preferences.addons[__name__].preferences

    if not preferences.use_submenu:
        bpy.types.TOPBAR_MT_file_import.append(menu_func_xmodel_import)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_xanim_import)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_xmodel_export)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_xanim_export)
    else:
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import_submenu)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export_submenu)

    from . import shared as shared
    shared.plugin_preferences = preferences

def submenu_reloader_unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_xmodel_import)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_xanim_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_xmodel_export)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_xanim_export)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_submenu)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_submenu)


