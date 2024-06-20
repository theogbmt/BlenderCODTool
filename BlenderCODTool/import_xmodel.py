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

# <pep8 compliant>

import os
import bpy
import bmesh
import array
from mathutils import *
from math import *
from bpy_extras.image_utils import load_image
from mathutils import Vector

from . import shared as shared
from .PyCoD import xmodel as XModel


def get_armature_for_object(ob):
    '''
    Get the armature for a given object.
    If the object *is* an armature, the object itself is returned.
    '''
    if ob is None:
        return None

    if ob.type == 'ARMATURE':
        return ob

    return ob.find_armature()


def get_armature_modifier_for_object(ob):
    for mod in ob.modifiers:
        if mod.type == 'ARMATURE':
            return mod
    return None


def reassign_children(ebs, bone1, bone2):
    for child in bone2.children:
        kid = ebs[child.name]
        kid.parent = bone1

    ebs.remove(bone2)


def join_objects(obs):
    scene = bpy.context.scene
    context = bpy.context.copy()
    context['active_object'] = obs[0]
    context['selected_objects'] = obs

    editable_bases = [scene.object_bases[ob.name] for ob in obs]
    context['selected_editable_bases'] = editable_bases
    bpy.ops.object.join(context)


def join_armatures(skel1_ob, skel2_ob, skel2_mesh_obs):
    skel2_mesh_matrices = [mesh.matrix_world.copy() for mesh in skel2_mesh_obs]

    join_objects([skel1_ob, skel2_ob])

    # Ensure that the context is correct
    bpy.context.render_layer.objects.active = skel1_ob
    skel1_ob.select_set(state=True)

    bpy.ops.object.mode_set(mode='EDIT')
    ebs = skel1_ob.data.edit_bones

    # Reassign all children for any bones that were present in both skeletons
    for bone in ebs:
        try:
            t = ebs[bone.name + ".001"]
            reassign_children(ebs, bone, t)
        except:
            pass

    # Remove the move the duplicates
    for bone in ebs:
        if(bone.name.endswith(".001")):
            ebs.remove(bone)

    if 'j_gun' in ebs and 'tag_weapon' in ebs:
        ebs['j_gun'].parent = ebs['tag_weapon']
    elif 'tag_weapon' in ebs and 'tag_weapon_right' in ebs:
        ebs['tag_weapon'].parent = ebs['tag_weapon_right']

    bpy.ops.object.mode_set(mode='OBJECT')

    # Update the matrices and armature modifier for the mesh objects
    for mesh_ob, matrix in zip(skel2_mesh_obs, skel2_mesh_matrices):
        mesh_ob.matrix_world = matrix
        mod = get_armature_modifier_for_object(mesh_ob)
        if mod is not None:
            # Update the existing armature modifier
            mod.object = skel1_ob
        else:
            # Add a new armature modifier
            mod = mesh_ob.modifiers.new('Armature Rig', 'ARMATURE')
            mod.object = skel1_ob
            mod.use_bone_envelopes = False
            mod.use_vertex_groups = True


def load(self, context,
         filepath,
         global_scale=1.0,
         apply_unit_scale=False,
         use_single_mesh=True,
         use_dup_tris=True,
         use_custom_normals=True,
         use_vertex_colors=True,
         use_armature=True,
         use_parents=True,
         attach_model=False,
         merge_skeleton=False,
         use_image_search=True):

    # Apply unit conversion factor to the scale
    if apply_unit_scale:
        global_scale *= shared.calculate_unit_scale_factor(context.scene)

    target_scale = global_scale

    if use_armature is False:
        attach_model = False

    skel_old = get_armature_for_object(context.active_object)
    if skel_old is None:
        attach_model = False

    if not attach_model:
        merge_skeleton = False

    split_meshes = not use_single_mesh
    load_images = True

    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Check if there are any objects in the scene
    if bpy.context.scene.objects:
        # Set the first object in the scene as the active object
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
    else:
        # If there are no objects in the scene, create a new empty object and set it as active
        bpy.ops.object.empty_add()
        bpy.context.view_layer.objects.active = bpy.context.active_object

    # Check if an active object is set
    if bpy.context.view_layer.objects.active:
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print("No active object selected or created. Please ensure there are objects in the scene.")

    # Load the model
    model_name = os.path.basename(filepath)
    model = XModel.Model(('.').join(model_name.split('.')[:-1]))

    ext = os.path.splitext(filepath)[-1].upper()
    if ext == '.XMODEL_BIN':
        LoadModelFile = model.LoadFile_Bin
    else:
        LoadModelFile = model.LoadFile_Raw

    LoadModelFile(filepath, split_meshes=split_meshes)

    # Materials
    materials = []
    material_images = {}

    for material in model.materials:
        mat = bpy.data.materials.get(material.name)
        if mat is None:
            print("Adding material '%s'" % material.name)
            mat = bpy.data.materials.new(name=material.name)

            if load_images:
                deferred_textures = []
                for image_type, image_name in material.images.items():
                    if image_name not in material_images:
                        search_dir = os.path.dirname(filepath)
                        image = load_image(image_name,
                                           dirname=search_dir,
                                           recursive=use_image_search,
                                           check_existing=True)
                        if image is None:
                            print("Failed to load image: '%s'" % image_name)
                            image = load_image(image_name,
                                               dirname=None,
                                               recursive=False,
                                               check_existing=True,
                                               place_holder=True)
                        material_images[image_name] = image
                    elif image_name in bpy.data.images:
                        image = bpy.data.images[image_name]
                    else:
                        image = material_images[image_name]
        else:
            if mat not in materials:
                print("Material '%s' already exists!" % material.name)
        materials.append(mat)

    # Meshes
    mesh_objs = []
    for sub_mesh in model.meshes:
        if split_meshes is False:
            sub_mesh.name = "%s_mesh" % model.name
        print("Creating mesh: '%s'" % sub_mesh.name)
        mesh = bpy.data.meshes.new(sub_mesh.name)
        bm = bmesh.new()

        # Add UV Layers
        uv_layer = bm.loops.layers.uv.new("UVMap")

        # Add Vertex Color Layer
        if use_vertex_colors:
            vert_color_layer = bm.loops.layers.color.new("Color")

        # Add Verts
        for vert in sub_mesh.verts:
            bm.verts.new(Vector(vert.offset) * target_scale)
        bm.verts.ensure_lookup_table()

        dup_faces = []
        dup_verts = []
        dup_verts_mapping = [None] * len(sub_mesh.verts)
        used_faces = []
        loop_normals = []
        material_usage_counts = [0] * len(materials)

        def setup_tri(f):
            material_index = face.material_id
            f.material_index = material_index
            material_usage_counts[material_index] += 1

            for loop_index, loop in enumerate(f.loops):
                face_index_loop = face.indices[loop_index]
                loop_normals.append(face_index_loop.normal)
                uv = Vector(face_index_loop.uv)
                uv.y = 1.0 - uv.y
                loop[uv_layer].uv = uv
                if use_vertex_colors:
                    loop[vert_color_layer] = face_index_loop.color

            used_faces.append(face)

        unused_faces = []

        vert_count = len(sub_mesh.verts)
        for face_index, face in enumerate(sub_mesh.faces):
            tmp = face.indices[2]
            face.indices[2] = face.indices[1]
            face.indices[1] = tmp

            indices = [bm.verts[index.vertex] for index in face.indices]

            try:
                f = bm.faces.new(indices)
            except ValueError:
                unused_faces.append(face)

                if not face.isValid():
                    print("TRI %d is invalid! %s" %
                          (face_index, [index.vertex for index in face.indices]))
                    continue

                for index in face.indices:
                    vert = index.vertex
                    if dup_verts_mapping[vert] is None:
                        dup_verts_mapping[vert] = len(dup_verts) + vert_count
                        dup_verts.append(sub_mesh.verts[vert])
                    index.vertex = dup_verts_mapping[vert]
                dup_faces.append(face)
            else:
                setup_tri(f)

        for face in unused_faces:
            sub_mesh.faces.remove(face)

        if use_dup_tris:
            for vert in dup_verts:
                bm.verts.new(Vector(vert.offset) * target_scale)
            bm.verts.ensure_lookup_table()

            for face in dup_faces:
                indices = [bm.verts[index.vertex] for index in face.indices]
                try:
                    f = bm.faces.new(indices)
                except ValueError:
                    pass
                else:
                    setup_tri(f)

        deform_layer = bm.verts.layers.deform.new()
        for vert_index, vert in enumerate(sub_mesh.verts):
            for bone, weight in vert.weights:
                bm.verts[vert_index][deform_layer][bone] = weight

        if use_dup_tris:
            offset = len(sub_mesh.verts)
            for vert_index, vert in enumerate(dup_verts):
                for bone, weight in vert.weights:
                    bm.verts[vert_index + offset][deform_layer][bone] = weight

        for mat in materials:
            mesh.materials.append(mat)

        bm.to_mesh(mesh)

        material_index = 0
        material_usage_index = 0
        for material in mesh.materials:
            if material_usage_counts[material_usage_index] == 0:
                mesh.materials.pop(index=material_index)
            else:
                material_index += 1
            material_usage_index += 1

        if use_custom_normals:
            calculate_split_normals(mesh)
            mesh.validate(clean_customdata=False)
            clnors = array.array('f', [0.0] * (len(mesh.loops) * 3))
            mesh.loops.foreach_get("normal", clnors)

            polygon_count = len(mesh.polygons)
            mesh.polygons.foreach_set("use_smooth", [True] * polygon_count)

            mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
        else:
            mesh.validate()

            polygon_count = len(mesh.polygons)
            mesh.polygons.foreach_set("use_smooth", [True] * polygon_count)

            mesh.calc_normals()

        if split_meshes:
            obj_name = "%s_%s" % (model.name, mesh.name)
        else:
            obj_name = model.name

        obj = bpy.data.objects.new(obj_name, mesh)
        mesh_objs.append(obj)

        scene.collection.objects.link(obj)
        view_layer.objects.active = obj

        for bone in model.bones:
            obj.vertex_groups.new(name=bone.name.lower())

        if load_images:
            material_image_map = [None] * len(model.materials)
            for index, material in enumerate(model.materials):
                if 'color' in material.images:
                    color_map = material.images['color']
                    if color_map in bpy.data.images:
                        material_image_map[index] = bpy.data.images[color_map]

    if use_armature:
        armature = bpy.data.armatures.new("%s_amt" % model.name)
        armature.display_type = "STICK"

        skel_obj = bpy.data.objects.new("%s_skel" % model.name, armature)
        skel_obj.show_in_front = True

        scene.collection.objects.link(skel_obj)
        view_layer.objects.active = skel_obj

        bpy.ops.object.mode_set(mode='EDIT')

        for bone in model.bones:
            edit_bone = armature.edit_bones.new(bone.name.lower())
            edit_bone.use_local_location = False

            offset = Vector(bone.offset) * target_scale
            axis = Vector(bone.matrix[1]) * target_scale
            roll = Vector(bone.matrix[2])

            edit_bone.head = offset
            edit_bone.tail = offset + axis
            edit_bone.align_roll(roll)

            if bone.parent != -1:
                parent = armature.edit_bones[bone.parent]
                if self.use_parents is True:
                    edit_bone.parent = parent

        bpy.ops.object.mode_set(mode='OBJECT')

        for mesh_obj in mesh_objs:
            mesh_obj.parent = skel_obj
            modifier = mesh_obj.modifiers.new('Armature Rig', 'ARMATURE')
            modifier.object = skel_obj
            modifier.use_bone_envelopes = False
            modifier.use_vertex_groups = True

        if attach_model and skel_old is not None:
            skel_obj.select_set(True)
            skel_old.select_set(True)
            view_layer.objects.active = skel_old
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.join()
            skel_obj.select_set(False)
            skel_old.select_set(False)

            if merge_skeleton:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.merge()
                bpy.ops.object.mode_set(mode='OBJECT')

    #return {'FINISHED'}

def manual_calc_normal(face):
    """ Manually calculate the normal for a face """
    verts = face.verts
    if len(verts) < 3:
        return Vector((0.0, 0.0, 0.0))
    
    v0, v1, v2 = verts[:3]
    edge1 = v1.co - v0.co
    edge2 = v2.co - v0.co
    normal = edge1.cross(edge2).normalized()
    return normal

def calculate_face_normals(bm):
    """ Calculate the normal for each face """
    for face in bm.faces:
        face.normal = manual_calc_normal(face)

def calculate_split_normals(mesh):
    # Ensure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a BMesh object from the mesh data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Calculate face normals
    calculate_face_normals(bm)

    # Prepare a list to store calculated loop normals
    loop_normals = []

    # Calculate split normals
    for face in bm.faces:
        face_normal = face.normal
        for loop in face.loops:
            vertex = loop.vert
            edge = loop.edge

            if edge.smooth:
                normal_sum = Vector((0.0, 0.0, 0.0))
                linked_faces_count = 0
                for linked_face in vertex.link_faces:
                    normal_sum += linked_face.normal
                    linked_faces_count += 1
                if linked_faces_count > 0:
                    loop_normal = (normal_sum / linked_faces_count).normalized()
            else:
                loop_normal = face_normal

            loop_normals.append(loop_normal)

    # Assign calculated normals to the mesh
    mesh.normals_split_custom_set(loop_normals)
    
    # Update the mesh to apply changes
    mesh.update()
    
    # Free BMesh
    bm.free()
