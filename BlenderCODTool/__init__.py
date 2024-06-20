# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# hello from bigman

bl_info = {
    "name": "BlenderCODTool 4.1",
    "author": "( 4.1 ) bigmanting ( 3.0 ) Ma_rv ( 2.8 ) CoDEmanX, Flybynyt, SE2Dev",
    "version": (0, 9, 2),
    "blender": (4, 1, 0),
    "location": "File > Import  |  File > Export",
    "description": "Import/Export XModels and XAnims",
    "wiki_url": "https://github.com/theogbmt/BlenderCODTool",
    "tracker_url": "https://github.com/theogbmt/BlenderCODTool/issues/",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

import bpy

##################################################
############# ALX MODULE AUTO-LOADER #############
import os
import importlib

folder_blacklist = ["__pycache__", "blendercodtool_updater"]
file_blacklist = ["__init__.py", "addon_updater_ops", "addon_updater.py"]

addon_folders = list([__path__[0]])
addon_folders.extend( [os.path.join(__path__[0], folder_name) for folder_name in os.listdir(__path__[0]) if ( os.path.isdir( os.path.join(__path__[0], folder_name) ) ) and (folder_name not in folder_blacklist) ] )

addon_files = [[folder_path, file_name[0:-3]] for folder_path in addon_folders for file_name in os.listdir(folder_path) if (file_name not in file_blacklist) and (file_name.endswith(".py"))]

for folder_file_batch in addon_files:
    if (os.path.basename(folder_file_batch[0]) == os.path.basename(__path__[0])):
        file = folder_file_batch[1]

        if (file not in locals()):
            import_line = f"from . import {file}"
            exec(import_line)
        else:
            reload_line = f"{file} = importlib.reload({file})"
            exec(reload_line)
    
    else:
        if (os.path.basename(folder_file_batch[0]) != os.path.basename(__path__[0])):
            file = folder_file_batch[1]

            if (file not in locals()):
                import_line = f"from . {os.path.basename(folder_file_batch[0])} import {file}"
                exec(import_line)
            else:
                reload_line = f"{file} = importlib.reload({file})"
                exec(reload_line)


import inspect

class_blacklist = ["PSA_UL_SequenceList"]

bpy_class_object_list = tuple(bpy_class[1] for bpy_class in inspect.getmembers(bpy.types, inspect.isclass) if (bpy_class not in class_blacklist))
alx_class_object_list = tuple(alx_class[1] for file_batch in addon_files for alx_class in inspect.getmembers(eval(file_batch[1]), inspect.isclass) if issubclass(alx_class[1], bpy_class_object_list) and (not issubclass(alx_class[1], bpy.types.WorkSpaceTool)))

AlxClassQueue = alx_class_object_list

def AlxRegisterClassQueue():
    for AlxClass in AlxClassQueue:
        try:
            bpy.utils.register_class(AlxClass)
        except:
            try:
                bpy.utils.unregister_class(AlxClass)
                bpy.utils.register_class(AlxClass)
            except:
                pass
def AlxUnregisterClassQueue():
    for AlxClass in AlxClassQueue:
        try:
            bpy.utils.unregister_class(AlxClass)
        except:
            print("Can't Unregister", AlxClass)

##################################################

from .BCT_utilities import submenu_reloader_register, submenu_reloader_unregister
from . import addon_updater_ops

def register():
    try:
        addon_updater_ops.register(bl_info)
    except:
        pass

    AlxRegisterClassQueue()

    submenu_reloader_register()

def unregister():
    addon_updater_ops.unregister()

    AlxUnregisterClassQueue()

    submenu_reloader_unregister()

if __name__ == "__main__":
    register()
