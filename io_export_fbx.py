#-------------------------------------------------------------------------------
# Name:        io_export_fbx
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

class CMskExportFbx(bpy.types.Operator):
##class CMskExportFbx():
    bl_idname = "masak.msk_export_fbx"
    bl_label = "msk_export_fbx"
    bl_description = "Export Fbx for unity"
    bl_context = "objectmode"


##    @classmethod
##    def poll(cls, context):
##        return context.object is not None


    def execute(self, context):
        # Find the Blender output file
        #import os
        #outfile = os.getenv("UNITY_BLENDER_EXPORTER_OUTPUT_FILE")
        outfile = bpy.path.abspath("//") + "tmp.fbx"

        # Do the conversion
        print("Starting blender to FBX conversion " + outfile)
        import math
        from mathutils import Matrix
        # -90 degrees
        mtx4_x90n = Matrix.Rotation(-math.pi / 2.0, 4, 'X')

        class FakeOp:
            def report(self, tp, msg):
                print("%s: %s" % (tp, msg))

        io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile,
        global_matrix=mtx4_x90n,
        use_selection = True,
        batch_mode='OFF',

        object_types={'EMPTY', 'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        use_anim=True,
        use_anim_optimize=False,
        anim_optimize_precision=6,
        use_anim_action_all=True,
        use_metadata=True,
        path_mode='AUTO',
        use_mesh_edges=True,
        use_rotate_workaround=False,
        use_default_take=True)
        # I don't think HQ normals are supported in the current exporter

        print("Finished blender to FBX conversion " + outfile)



        import os
        # contains the '\'
        curdir = bpy.path.abspath("//")
        abspath = curdir + "_copy.bat"
        print(abspath)
        os.popen("cmd /C " + abspath + " " + curdir)


        return{'FINISHED'}


def main():
    instance = CMskExportFbx()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
