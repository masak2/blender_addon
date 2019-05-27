#-------------------------------------------------------------------------------
# Name:        obj_remove_ignoreautoweight_vg
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
from masak.util_various import *

#breakpoint = bpy.types.bp.bp

class CMskRemoveIgnoreAutoWeightVG(bpy.types.Operator):
##class CMskRemoveIgnoreAutoWeightVG():
    bl_idname = "masak.msk_remove_ignoreautoweight_vg"
    bl_label = "msk_remove_ignoreautoweight_vg"
    bl_description = "Remove Deform VertexGroup Weight from vertices in '_ignore_autoweight' vertex group"
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

        src_objs = context.selected_objects
        for obj in src_objs:
            if obj.type != 'MESH':
                continue

            need_remove = False
            vg_index = -1
            for vg in obj.vertex_groups:
                if vg.name == "_ignore_autoweight":
                    need_remove = True
                    vg_index = vg.index
                    break
            if need_remove == False:
                continue

            # get vertices which are contained in '_ignore_autoweight' vertex group
            mv_index_list = []
            mesh = obj.data
            for mv in mesh.vertices:
                for vge in mv.groups:
                    if vge.group == vg_index:
                        mv_index_list.append(mv.index)

            if len(mv_index_list) == 0:
                continue

            for vg in obj.vertex_groups:
                if vg.name.startswith("def_"):
                    vg.remove(mv_index_list)

        return{'FINISHED'}


def main():
    instance = CMskRemoveIgnoreAutoWeightVG()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
