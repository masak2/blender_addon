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
import mathutils
import io_scene_fbx.export_fbx
from masak.util_various import *

breakpoint = bpy.types.bp.bp

class CMskPreRemoveImage(bpy.types.Operator):
##class CMskPreRemoveImage():
    bl_idname = "masak.msk_io_pre_remove_image"
    bl_label = "msk_io_pre_remove_image"
    bl_description = "Remove image from selected objects"
    bl_context = "objectmode"

    def execute(self, context):
        objs = context.selected_objects
        fbx_objs = []
        for obj in objs:
            if obj.type == 'MESH':
                fbx_objs.append(obj)

        # remove images
        for obj in fbx_objs:
            for umflayer in obj.data.uv_textures:
                for umface in umflayer.data:
                    umface.image = None


        return{'FINISHED'}


def main():
    instance = CMskPreRemoveImage()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
