#-------------------------------------------------------------------------------
# Name:        cur_generate_hair
# Purpose:
#
# Author:      masak
#
# Created:     07/10/2011
# Copyright:   (c) masak 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import bpy
import mathutils
from masak.util_various import *


#breakpoint = bpy.types.bp.bp

#///////////////////////////////////////////////////////////////////////////////
#   make hair curves based on template mesh
#///////////////////////////////////////////////////////////////////////////////
class CMskGenerateHairCurve(bpy.types.Operator):
    bl_idname="masak.msk_gen_hair_curve"
    bl_label = "msk_gen_hair_curve"
    bl_description = "Make Curves along guide mesh, and set hair, rig, select sim_hair"


    class VERTEX_GROUP_SET:
        def __init__(self):
            # array of vector
            self.arr_topco= []
            self.arr_btmco= []
            self.name = ""
            self.total= 0

    class CURVE_INFO:
        def __init__(self):
            self.co0 = [0,0,0]
            self.co1 = [0,0,0]
            self.name = ""
            self.object= None
            self.meshobj_name= ""
            self.meshobj = None


    def execute(self, context):
        visible_objects = context.visible_objects

        obj_sim_hair = None
        for obj in visible_objects:
            if obj.name == "tmp_hair_guide":
                obj_sim_hair = obj
                break

        if obj_sim_hair == None:
            msk_util_warning("tmp_hair_guide")
            return {"FINISHED"}

        self.setup_hair_impl( context, obj_sim_hair, context.scene.hair_front_total, "hair_f")
        self.setup_hair_impl( context, obj_sim_hair, context.scene.hair_side_total, "hair_s")
        self.setup_hair_impl( context, obj_sim_hair, context.scene.hair_back0_total, "hair_b0")
        self.setup_hair_impl( context, obj_sim_hair, context.scene.hair_back1_total, "hair_b1")


        return {"FINISHED"}

    def setup_hair_impl(self, context, obj_sim_hair, curve_total, hair_category):
        mesh = obj_sim_hair.data
        vertices = mesh.vertices

        # get vertex group index pair( top and btm
        # top btm top btm...
        aiVGIndex = []
        iVGIndexTotal = 20
        for i in range(0,iVGIndexTotal):
            aiVGIndex.append(-1)


        for vg in obj_sim_hair.vertex_groups:
            if vg.name.startswith(hair_category):
                asz = vg.name.split('.')

                index = int(asz[1])
                if asz[2] == "top":
                    index = index * 2
                elif asz[2] == "btm":
                    index = index * 2 +1
                else:
                    msk_util_warning("invalid vertexgroup name = " + vg.name)
                    continue

                if index < iVGIndexTotal:
                    aiVGIndex[index] = vg.index
                else:
                    msk_util_warning("index out of range =" + vg.name)

        # check that this array is valid or not
        iInvalidTotal = 0
        n = int(iVGIndexTotal/2)
        for i in range(0,n):
            top = aiVGIndex[2*i]
            btm = aiVGIndex[2*i+1]
            if top == -1:
                iInvalidTotal += 1
            if btm == -1:
                iInvalidTotal += 1
            if (top == -1 and btm != -1) or (top != -1 and btm == -1):
                msk_util_warning("invalid aiVGIndex")
                return

        # trim array( -1 is invalid
        for i in range(0, iInvalidTotal):
            aiVGIndex.remove(-1)

        oVertexGroupSet = self.VERTEX_GROUP_SET()
        oVertexGroupSet.total = int(len(aiVGIndex) / 2)
        for i in range(0, oVertexGroupSet.total):
            oVertexGroupSet.arr_btmco.append(None)
            oVertexGroupSet.arr_topco.append(None)

        # get vertex coordinates
        world_location = mathutils.Vector((0,0,0))
##        print("location =")
##        print(obj_sim_hair.location)
##        lm = obj_sim_hair.matrix_local
##        print(lm)
        wm = obj_sim_hair.matrix_world
##        print(wm)
        world_location[0] = wm[3][0]
        world_location[1] = wm[3][1]
        world_location[2] = wm[3][2]
        for iVGIndex in aiVGIndex:
##            print("iVGIndex=" + str(iVGIndex))
            bTop = True
            vg = obj_sim_hair.vertex_groups[iVGIndex]
##            print(vg)
            name_len = len(vg.name)
            szcurve_index = vg.name[name_len-7:name_len-4]# _???.top
##            print(szcurve_index)
            curve_index = int(szcurve_index)
            if vg.name.endswith("top"):
                bTop = True
            else:
                bTop = False

            bFind = False
            for vm in vertices:
                for vge in vm.groups:
                    if vge.group == iVGIndex:
                        bFind = True

                        #curve_info = aoCurveInfo[curve_index]


                        #curve_info.name = "Bezier_" + vg.name[0: name_len-4]# remove .top or .btm
##                        print(vg.name)
##                        print(curve_index)
##                        print(vm.co)
                        co = mathutils.Vector((0,0,0))
                        if bTop:
                            for i in range(0,3):
                                co[i] = vm.co[i] + world_location[i]
                            oVertexGroupSet.arr_topco[curve_index] = co
##                            print("top coordinate")
##                            print(curve_info.co0)
                        else:
                            for i in range(0,3):
                                co[i] = vm.co[i] + world_location[i]
                            oVertexGroupSet.arr_btmco[curve_index] = co
##                            print("btm oocridnate")
##                            print(curve_info.co1)
                        break
                if bFind:
                    break
##        print("aoCurveInfo Total = " + str(len(aoCurveInfo)))
##        if len(aoCurveInfo) >= 3:
##            self.create_curve(context, aoCurveInfo[2], world_location)
##        print("vertex coordinate")
##        for i in range(0, oVertexGroupSet.total):
##            print("%03d" % i)
##            print(oVertexGroupSet.arr_topco[i])
##            print(oVertexGroupSet.arr_btmco[i])

        # calc actual coordinates
        aoCurveInfo = []
        for i in range(0,curve_total):
            aoCurveInfo.append(self.CURVE_INFO())

        # at first, calc array of lengths between vertices
        n = oVertexGroupSet.total- 1
        aiLenTop = []
        aiLenBtm = []
        len_total_top = 0.0
        len_total_btm = 0.0
        for i in range(0,n):
            v0 = oVertexGroupSet.arr_topco[i]
            v1 = oVertexGroupSet.arr_topco[i+1]
            vdif = v0 - v1
            length = vdif.length
            len_total_top += length
            aiLenTop.append(length)

            v0 = oVertexGroupSet.arr_btmco[i]
            v1 = oVertexGroupSet.arr_btmco[i+1]
            vdif = v0 - v1
            length = vdif.length
            len_total_btm += length
            aiLenBtm.append(length)


##        print("aiLentotal")
##        print(len_total_top)
##        print("//")
        for leng in aiLenTop:
            print(leng)

        curve_index = 0
        vertex_total =oVertexGroupSet.total
##        slope = (oVertexGroupSet.total - 1) / (curve_total - 1)
        for curve_info in aoCurveInfo:
            # top

            if curve_index == 0:
                curve_info.co0 = oVertexGroupSet.arr_topco[0]
            elif curve_index == curve_total - 1:
                curve_info.co0 = oVertexGroupSet.arr_topco[vertex_total-1]
            else:
                x = len_total_top * curve_index / (curve_total - 1)
                vertex_index0 = 0
                vertex_index1 = 0
                coef = 0.0
                len0 = 0.0
                len1 = aiLenTop[0]
                for j in range(0, len(aiLenTop)):
                    print("len0=" + str(len0) + " x=" + str(x) + " len1=" + str(len1))
                    if len0 <= x and x < len1:
                        vertex_index0 = j
                        vertex_index1 = j + 1
                        coef = (x - len0) / aiLenTop[j]
                        break
                    len0 += aiLenTop[j]
                    len1 += aiLenTop[j+1]
                v0 = oVertexGroupSet.arr_topco[vertex_index0]
                v1 = oVertexGroupSet.arr_topco[vertex_index1]
                curve_info.co0 = v0.lerp(v1, coef)

##            y = slope * curve_index
##            vertex_index0 = math.floor(y)
##            vertex_index1 = min(vertex_index0 + 1, oVertexGroupSet.total-1)
##            coef = y - vertex_index0


            # bottom
            if curve_index == 0:
                curve_info.co1 = oVertexGroupSet.arr_btmco[0]
            elif curve_index == curve_total - 1:
                curve_info.co1 = oVertexGroupSet.arr_btmco[vertex_total-1]
            else:
                x = len_total_btm * curve_index / (curve_total - 1)
                vertex_index0 = 0
                vertex_index1 = 0
                coef = 0.0
                len0 = 0.0
                len1 = aiLenBtm[0]
                for j in range(0,len(aiLenBtm)):
                    if len0 <= x and x < len1:
                        vertex_index0 = j
                        vertex_index1 = j+1
                        coef = (x - len0) / aiLenBtm[j]
                        break
                    len0 += aiLenBtm[j]
                    len1 += aiLenBtm[j+1]

                v0 = oVertexGroupSet.arr_btmco[vertex_index0]
                v1 = oVertexGroupSet.arr_btmco[vertex_index1]
                curve_info.co1 = v0.lerp(v1, coef)

            curve_info.name = "cur_" + hair_category + ('.%03d' % curve_index)
            curve_info.meshobj_name = "o_" + hair_category + ('.%03d' % curve_index)
            curve_index += 1

##        print("//")
##        print("interpolated coordinate")
##        print("//")
##        for curve_info in aoCurveInfo:
##            print(curve_info.meshobj_name)
##            print(curve_info.co0)
##            print(curve_info.co1)
##        return

        # set curve obj and mesh obj if exists
        for curve_info in aoCurveInfo:
            if curve_info.name in bpy.data.objects:
                curve_info.object = bpy.data.objects[curve_info.name]
            if curve_info.meshobj_name in bpy.data.objects:
                curve_info.meshobj = bpy.data.objects[curve_info.meshobj_name]
##            print(curve_info.object)
##            print(curve_info.meshobj)
##        return
        # just create curve
        for curve_info in aoCurveInfo:
            # check that the curve already exists or not
            if curve_info.object == None:
                self.create_curve(context, curve_info)
                self.tweak_curve(context, curve_info) # if need


        # tweak all
        #for curve_info in aoCurveInfo:
        #    self.tweak_curve(context, curve_info)

        # set hair mesh obj to curve modifier
        # which corresponds to curve obj which has same name
        msk_util_noselect()
        for curve_info in aoCurveInfo:
            self.set_hairobj_curve_modifier( context, curve_info )
            self.set_hairobj_mirror_modifier(context, curve_info)
            self.set_hairobj_subsurf_modifier(context, curve_info)

    #///////////////////////////////////////////////////////////////////////////
    #   just create a curve object and
    #   set obj name and curve name
    #
    #   curve :
    #   curve_info : CURVE_INFO
    #///////////////////////////////////////////////////////////////////////////
    def create_curve(self, context, curve_info):
        bpy.ops.curve.primitive_bezier_curve_add(
        )
        obj_curve = context.active_object

        obj_curve.select = False

        curve_info.object = obj_curve
        if obj_curve.type != 'CURVE':
            msk_util_warning("this is not curve object = " + curve_info.name)
            return

        curve_name = curve_info.name
        obj_curve.name = curve_name

        curve = obj_curve.data
        curve.name = curve_name

    #///////////////////////////////////////////////////////////////////////////
    #   set coordinates of a curve
    #
    #   context :
    #   curve_info : CURVE_INFO
    #///////////////////////////////////////////////////////////////////////////
    def tweak_curve(self, context, curve_info):
        obj_curve = curve_info.object
        if obj_curve.type != 'CURVE':
            msk_util_warning("this is not curve object = " + curve_info.name)
            return

        curve = obj_curve.data
        for spline in curve.splines:
            if len(spline.bezier_points) != 2:
                msk_util_warning("invalid bezier curve ")
                break

##        print(curve_info.co0)
##        print(curve_info.co1)
        ## start
##        print("bezier_point =" + str(len(curve.splines[0].bezier_points)))
        bsp0 = curve.splines[0].bezier_points[0]
        vpos0 = mathutils.Vector(curve_info.co0)
        for i in range(0,3):
            bsp0.co[i] = curve_info.co0[i]

        ## end
        bsp1 = curve.splines[0].bezier_points[1]
        vpos1 = mathutils.Vector(curve_info.co1)
        for i in range(0,3):
            bsp1.co[i] = curve_info.co1[i]

        # handle is relative coordinate
        v0to1 = vpos1 - vpos0
        v0to1[2] = 0.0 # hack
        v0to1.normalize()
##        print(v0to1)
        vtmppos = mathutils.Vector((0,0,0))

        v0to1 *= 0.1 # tweak the length
        bsp0.handle_right_type = 'FREE'
        bsp0.handle_left_type = 'FREE'

        vtmppos = vpos0 + v0to1
        for i in range(0,3):
            bsp0.handle_right[i] = vtmppos[i]

        vtmppos = vpos0 - v0to1
        for i in range(0,3):
            bsp0.handle_left[i] = vtmppos[i]

        bsp0.handle_left_type = 'ALIGNED'
        bsp0.handle_right_type = 'ALIGNED'

        bsp1.handle_left_type = 'FREE'
        bsp1.handle_right_type = 'FREE'
        vup = mathutils.Vector((0,0,0.1))

        vtmppos = vpos1 + vup
        for i in range(0,3):
            bsp1.handle_left[i] = vtmppos[i]
        vtmppos = vpos1 -vup
        for i in range(0,3):
            bsp1.handle_right[i] = vtmppos[i]

        bsp1.handle_left_type = 'ALIGNED'
        bsp1.handle_right_type = 'ALIGNED'

    #///////////////////////////////////////////////////////////////////////////
    #   set hairobj a curve modifier
    #
    #   context :
    #   curve_info : CURVE_INFO
    #///////////////////////////////////////////////////////////////////////////
    def set_hairobj_curve_modifier(self, context, curve_info):
        if curve_info.meshobj == None:
            return
        msk_util_newmodifier_if_no_exist( curve_info.meshobj, "Curve", 'CURVE')

##            obj_hair.select = True
##            print(obj_hair.name)
##            bpy.ops.object.modifier_add(type='CURVE')
##            obj_hair.select = False

##        for i in range(0,3):
##            obj_hair.location[i] = 0.0

        for modifier in curve_info.meshobj.modifiers:
            if modifier.type == 'CURVE':
                modifier.object = curve_info.object
                modifier.deform_axis = 'POS_X'
                return

    def set_hairobj_mirror_modifier(self, context, curve_info):
        if curve_info.meshobj == None:
            return
        msk_util_newmodifier_if_no_exist( curve_info.meshobj, "Mirror", 'MIRROR')

    def set_hairobj_subsurf_modifier(self, context, curve_info):
        if curve_info.meshobj == None:
            return
        msk_util_newmodifier_if_no_exist( curve_info.meshobj, "Subsurf", 'SUBSURF')
        modifier = curve_info.meshobj.modifiers["Subsurf"]
        modifier.levels = 1
        modifier.render_levels = 2

def main():
    instance = CMskGenerateHairCurve()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
