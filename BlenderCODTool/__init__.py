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
    "version": (0, 9, 0),
    "blender": (4, 1, 0),
    "location": "File > Import  |  File > Export",
    "description": "Import/Export XModels and XAnims",
    "wiki_url": "https://github.com/theogbmt/BlenderCODTool",
    "tracker_url": "https://github.com/theogbmt/BlenderCODTool/issues/",
    "support": "COMMUNITY",
    "category": "Import-Export"
}



##################################################
############# ALX MODULE AUTO-LOADER #############
from typing import Iterable
import importlib
from os import sep as os_separator
from pathlib import Path


<<<<<<< HEAD
import bpy
from . import addon_updater_ops
=======
folder_blacklist = ["__pycache__"]
file_blacklist = ["__init__.py", "addon_updater_ops", "addon_updater.py"]
>>>>>>> 08cfbbc64ec5c5178e86e79d2efa63b4ecf5f362


init_path: Iterable[str]  = __path__
folder_name_blacklist: list[str]=("__pycache__") 
file_name_blacklist: list[str]=("__init__.py")
class_name_blacklist: list[str]=("PSA_UL_sequences")


addon_folders = set()
addon_files = set()

addon_path_iter = [ Path( init_path[0] ) ]
addon_path_iter.extend(Path( init_path[0] ).iterdir())

for folder_path in addon_path_iter:
    
    if ( folder_path.is_dir() ) and ( folder_path.exists() ) and ( folder_path.name not in folder_name_blacklist ):
        addon_folders.add( folder_path )

        for subfolder_path in folder_path.iterdir():
            if ( subfolder_path.is_dir() ) and ( subfolder_path.exists()):
                addon_path_iter.append( subfolder_path )
                addon_folders.add( subfolder_path )


addon_files = [[folder_path, file_name.name[0:-3]] for folder_path in addon_folders for file_name in folder_path.iterdir() if ( file_name.is_file() ) and ( file_name.name not in file_name_blacklist ) and ( file_name.suffix == ".py" )]

for folder_file_batch in addon_files:
    file = folder_file_batch[1]
    
    if (file not in locals()):
        relative_path = str(folder_file_batch[0].relative_to( init_path[0] ) ).replace(os_separator,"." )

        import_line = f"from . {relative_path if relative_path != '.' else ''} import {file}"
        exec(import_line)
    else:
        reload_line = f"{file} = importlib.reload({file})"
        exec(reload_line)


import inspect

bpy_class_object_list = tuple(bpy_class[1] for bpy_class in inspect.getmembers(bpy.types, inspect.isclass) if (bpy_class[0] not in class_name_blacklist))
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

def register():
<<<<<<< HEAD
    try:
        addon_updater_ops.register(bl_info)
    except:
        print("BlenderCODTools: addon_updater failed")

=======
>>>>>>> 08cfbbc64ec5c5178e86e79d2efa63b4ecf5f362
    AlxRegisterClassQueue()

    submenu_reloader_register()

def unregister():
    AlxUnregisterClassQueue()

    submenu_reloader_unregister()

if __name__ == "__main__":
    register()
