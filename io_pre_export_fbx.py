#-------------------------------------------------------------------------------
# Name:        io_pre_export_fbx
# Purpose:
#
# Author:      masak
#
# Created:     10/10/2011
# Copyright:   (c) masak 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import bpy
import mathutils
import io_scene_fbx.export_fbx
from masak.util_various import *

breakpoint = bpy.types.bp.bp

class CMskPreExportFbx(bpy.types.Operator):
##class CMskPreExportFbx():
    bl_idname = "masak.msk_pre_export_fbx"
    bl_label = "msk_pre_export_fbx"
    bl_description = "Call before Export Fbx for unity"
    bl_context = "objectmode"

    def execute(self, context):
        objs = context.selected_objects
        fbx_objs = []
        for obj in objs:
            if obj.type == 'MESH':
                fbx_objs.append(obj)


        for obj in fbx_objs:
            msk_util_select_only(obj.name)
            bpy.ops.object.transform_apply(scale = True)


        # duplicate and put them into layer 14
        src_objs = []
        src_objs = fbx_objs[:]
        fbx_objs = []
        for src_obj in src_objs:
            msk_util_select_only(src_obj.name)
            bpy.ops.object.duplicate()
            print(src_obj.name)
            dst_obj = context.selected_objects[0]
            dst_obj.name = "g" + src_obj.name
            msk_util_set_layer( dst_obj, 14)

            fbx_objs.append(dst_obj)


        # remove images
        for obj in fbx_objs:
            for umflayer in obj.data.uv_textures:
                for umface in umflayer.data:
                    umface.image = None


        # remove unnecessary modifiers
        for obj in fbx_objs:
            for mod in obj.modifiers:
                if mod.type == 'SOLIDIFY' or mod.type == 'SUBSURF' or mod.type == 'CLOTH':
                    obj.modifiers.remove(mod)


        # apply modifiers
        for obj in fbx_objs:
            msk_util_select_only(obj.name)
            for mod in obj.modifiers:
                if mod.type == 'ARRAY' or mod.type == 'CURVE' or mod.type == 'LATTICE' or mod.type == 'SHRINKWRAP':
                    bpy.ops.object.modifier_apply('DATA', mod.name)


        #
        scene = context.scene
        scene.layers[14] = True
        for obj in fbx_objs:
            context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            # this means deselect all
            bpy.ops.mesh.select_random()
            bpy.ops.mesh.select_all()
            need_dupli = False
            for i,vg in enumerate(obj.vertex_groups):
                if vg.name == "_dupli":
                    obj.vertex_groups.active_index = i
                    need_dupli = True
                    break

            if need_dupli:
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.duplicate_move()
                bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')

        # merge
        msk_util_noselect()
        except_obj = ["go_skirt", "go_hair"]
        for obj in fbx_objs:
            need_select = True
            for name in except_obj:
                if obj.name.startswith(name):
                    need_select = False
                    break
            obj.select = need_select


        scene.objects.active = fbx_objs[0]
        bpy.ops.object.join()
        context.active_object.name = "go_body"

        return{'FINISHED'}


def main():
    instance = CMskPreExportFbx()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
