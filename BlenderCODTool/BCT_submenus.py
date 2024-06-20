import bpy

from .BCT_import_operators import COD_MT_import_xmodel, COD_MT_import_xanim, COD_MT_export_xmodel, COD_MT_export_xanim

class COD_MT_import_submenu(bpy.types.Menu):
    bl_idname = "COD_MT_import_submenu"
    bl_label = "Call of Duty"

    def draw(self, context):
        menu_func_xmodel_import(self, context)
        menu_func_xanim_import(self, context)

class COD_MT_export_submenu(bpy.types.Menu):
    bl_idname = "COD_MT_export_submenu"
    bl_label = "Call of Duty"

    def draw(self, context):
        menu_func_xmodel_export(self, context)
        menu_func_xanim_export(self, context)

def menu_func_xmodel_import(self, context):
    self.layout.operator(COD_MT_import_xmodel.bl_idname,
                         text="CoD XModel (.XMODEL_EXPORT, .XMODEL_BIN)")

def menu_func_xanim_import(self, context):
    self.layout.operator(COD_MT_import_xanim.bl_idname,
                         text="CoD XAnim (.XANIM_EXPORT, .XANIM_BIN)")

def menu_func_xmodel_export(self, context):
    self.layout.operator(COD_MT_export_xmodel.bl_idname,
                         text="CoD XModel (.XMODEL_EXPORT, .XMODEL_BIN)")

def menu_func_xanim_export(self, context):
    self.layout.operator(COD_MT_export_xanim.bl_idname,
                         text="CoD XAnim (.XANIM_EXPORT, .XANIM_BIN)")

def menu_func_import_submenu(self, context):
    self.layout.menu(COD_MT_import_submenu.bl_idname, text="Call of Duty")

def menu_func_export_submenu(self, context):
    self.layout.menu(COD_MT_export_submenu.bl_idname, text="Call of Duty")