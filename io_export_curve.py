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

class CMskExportCurveInfo(bpy.types.Operator):
##class CMskExportBoneLengthInfo():
    bl_idname = "masak.msk_io_export_curveinfo"
    bl_label = "msk_io_export_curveinfo"
    bl_description = "Export Curve info to [filename].csv"
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
        basepath = "C:/WO/planner/parameter/map/" + basename
        curve_path = basepath + "_curve.csv"
        spline_path = basepath + "_spline.csv"
        bezier_path = basepath  + "_bezier.csv"
        print(curve_path)

        # get info

        fs_curve = open(curve_path, 'w')
        fs_curve.write("ID,SplineArr\n")

        fs_spline = open(spline_path, 'w')
        fs_spline.write("ID,PointArr\n")

        fs_bezier = open(bezier_path, 'w')
        fs_bezier.write("ID,Co.x,Co.y,Co.z,\
HandleLeft.x,HandleLeft.y,HandleLeft.z,\
HandleRight.x,HandleRight.y,HandleRight.z\n")
        idx_curve = 1
        idx_spline = 1
        idx_bezier = 1
        selectedobj = bpy.context.selected_objects
        for obj in selectedobj:
            curve = obj.data
            fs_curve.write("%i,[" % idx_curve)
            nSpline = len(curve.splines)
            for tmpidx in range(nSpline):
                if tmpidx == 0:
                    fs_curve.write("%i" % (tmpidx + idx_spline))
                else:
                    fs_curve.write("/%i" % (tmpidx + idx_spline))
            fs_curve.write("]\n")
            idx_curve += 1
            for spline in curve.splines:
                fs_spline.write("%i,[" % idx_spline)
                nBezier = len(spline.bezier_points)
                for tmpidx in range(nBezier):
                    if tmpidx == 0:
                        fs_spline.write("%i" % (tmpidx + idx_bezier))
                    else:
                        fs_spline.write("/%i" % (tmpidx + idx_bezier))
                fs_spline.write("]\n")
                idx_spline += 1
                for bsp in spline.bezier_points:
                    fs_bezier.write("%i,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % \
                    (idx_bezier,bsp.co[0],bsp.co[1],bsp.co[2],\
                        bsp.handle_left[0],bsp.handle_left[1],bsp.handle_left[2],
                        bsp.handle_right[0],bsp.handle_right[1],bsp.handle_right[2]))
                    idx_bezier += 1

        return{'FINISHED'}

def main():
    instance = CMskExportCurveInfo()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
