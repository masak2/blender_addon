#-------------------------------------------------------------------------------
# Name:        arm_switch_usedeform
# Purpose:
#
# Author:      masak
#
# Created:     26/10/2011
# Copyright:   (c) masak 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import bpy


#breakpoint = bpy.types.bp.bp

class CMskSwitchUseDeform(bpy.types.Operator):
##class CMskSwitchUseDeform():
    bl_idname = "masak.msk_arm_switch_usedeform"
    bl_label = "msk_arm_switch_usedeform"
    bl_description = "Switch Use Deform in a Layer"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        sel_objs = context.selected_objects
        src_objs = []
        for obj in sel_objs:
            if obj.type == 'ARMATURE':
                src_objs.append(obj)
        if len(src_objs) == 0:
            return{'CANCELED'}

        def_name_list = ["def", "DEF", "Ad_d", "Ad-d"]
        #switch_bone_layer = 24
        switch_bone_layer = context.scene.arm_switch_layer
        for obj in src_objs:
            arm = obj.data
            for bn in arm.bones:
                if bn.layers[switch_bone_layer] == False:
                    continue

                deform_bone = False
                for key in def_name_list:
                    if bn.name.startswith(key):
                        deform_bone = True
                        break
                if deform_bone:
                    bn.use_deform = not bn.use_deform


        return{'FINISHED'}


def main():
    instance = CMskSwitchUseDeform()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()