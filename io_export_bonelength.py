#-------------------------------------------------------------------------------
# Name:        io_export_bonelength
# Purpose:
#
# Author:      masak
#
# Created:     05/06/2012
# Copyright:   (c) masak 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import bpy
import mathutils
from masak.util_various import *
import os

#breakpoint = bpy.types.bp.bp

class CMskExportBoneLengthInfo(bpy.types.Operator):
##class CMskExportBoneLengthInfo():
    bl_idname = "masak.msk_io_export_bonelengthinfo"
    bl_label = "msk_io_export_bonelengthinfo"
    bl_description = "Export bonelength info to [filename].csv"
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

        #
        # export format
        #
        path = bpy.data.filepath
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        basename = basename.replace(".blend","")
        #path = dirname + "/" + basename + "_bonelength.csv"
        path = "C:/WO/planner/parameter/characters/" + basename + "_bonelength.csv"
        print(path)

        # get info

        fs = open(path, 'w')
        fs.write("ID,BoneName,Length,Connect\n")
        active_obj = context.active_object
        if active_obj.type == 'ARMATURE':
            index = 0
            for bone in active_obj.data.bones:
                if bone.name.startswith("def_") and bone.name.find("hair") != -1:
                    bonename = bone.name.replace(".","_")
                    fs.write("%i,%s,%f,%s\n" % (index, bonename, bone.length, bone.use_connect))
                    index += 1

        return{'FINISHED'}

def main():
    instance = CMskExportBoneLengthInfo()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
