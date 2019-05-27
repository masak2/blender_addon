#-------------------------------------------------------------------------------
# Name:        obj_generate_merged_hair
# Purpose:
#
# Author:      masak
#
# Created:     09/10/2011
# Copyright:   (c) masak 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import bpy
from masak.util_various import *

#breakpoint = bpy.types.bp.bp

class CMskCreateMergedHair(bpy.types.Operator):
##class CMskCreateMergedHair():
    bl_idname = "masak.msk_gen_merged_hair"
    bl_label = "msk_gen_merged_hair"
    bl_description = "Create Merged Hair MeshObject From Obj like curve"
    bl_context = "objectmode"

    def execute(self, context):
        msk_util_print(self.bl_idname)
        visible_objs = context.visible_objects


        # just duplicate o_hair_*
        for obj in visible_objs:
            if obj.name.startswith("o_hair_"):
                msk_util_noselect()
                obj.select = True
                bpy.ops.object.duplicate()

                # i think selected objects means one duplicated object
                # or is it better to use active_object ?
                for dupli_obj in context.selected_objects:
                    dupli_obj.name = "tmp" + dupli_obj.name


        # apply curve modifier to duplicated objects
        visible_objs = context.visible_objects
        for obj in visible_objs:
            if obj.name.startswith("tmpo_hair_"):
                for modif in dupli_obj.modifiers:
                    if modif.type == 'CURVE':
                        context.scene.objects.active = obj
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modif.name)
                        break


        # merge all duplicated objects to one hair object
        msk_util_noselect()
        visible_objs = context.visible_objects
        for obj in visible_objs:
            if obj.name.startswith("tmpo_hair_"):
                obj.select = True
                context.scene.objects.active = obj
        bpy.ops.object.join()

        hair_obj = None
        for merged_obj in context.selected_objects:
            merged_obj.name = "o_hair"
            merged_obj.data.name = "hair"
            hair_obj = merged_obj


        # add mirror modifier if no
        if hair_obj != None:
            msk_util_newmodifier_if_no_exist( hair_obj, "", 'MIRROR' )


        return{'FINISHED'}


def main():
    instance = CMskCreateMergedHair()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
