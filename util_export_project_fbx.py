#-------------------------------------------------------------------------------
# Name:        io_pre_remove_image
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

#breakpoint = bpy.types.bp.bp

class CMskExportProjectFbx(bpy.types.Operator):
##class CMskCountBone():
    bl_idname = "masak.msk_export_project_fbx"
    bl_label = "msk_export_project_fbx"
    bl_description = "Export Fbx"
    bl_context = "objectmode"

    def execute(self, context):
        objs = context.selected_objects
        src_objs = []
        for obj in objs:
            if obj.type == 'ARMATURE':
                src_objs.append(obj)
        if len(src_objs) > 0:
            obj = src_objs[0]
            armature = obj.data
            context.scene.bone_total = len(armature.bones)

            deform_total = 0
            for bn in armature.bones:
                if bn.use_deform:
                    deform_total += 1
            context.scene.deform_bone_total = deform_total


        return{'FINISHED'}


def main():
    instance = CMskExportProjectFbx()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
