import bpy

from .BCT_submenus import menu_func_import_submenu, menu_func_export_submenu, menu_func_xmodel_import, menu_func_xanim_export, menu_func_xanim_import, menu_func_xmodel_export

def submenu_reloader_register():
    #bpy.types.TOPBAR_MT_file_import.append(menu_func_xmodel_import)
    #bpy.types.TOPBAR_MT_file_import.append(menu_func_xanim_import)
    #bpy.types.TOPBAR_MT_file_export.append(menu_func_xmodel_export)
    #bpy.types.TOPBAR_MT_file_export.append(menu_func_xanim_export)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_submenu)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_submenu)

def submenu_reloader_unregister():
    #bpy.types.TOPBAR_MT_file_import.remove(menu_func_xmodel_import)
    #bpy.types.TOPBAR_MT_file_import.remove(menu_func_xanim_import)
    #bpy.types.TOPBAR_MT_file_export.remove(menu_func_xmodel_export)
    #bpy.types.TOPBAR_MT_file_export.remove(menu_func_xanim_export)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_submenu)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_submenu)


