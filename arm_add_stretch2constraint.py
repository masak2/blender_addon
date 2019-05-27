#-------------------------------------------------------------------------------
# Name:        arm_add_stretch2constraint
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

class CMskAddPoseStretchToConstraint(bpy.types.Operator):
##class CMskAddPoseStretchToConstraint():
    bl_idname = "masak.msk_add_posestrech2_constraint"
    bl_label = "msk_add_posestrech2_constraint"
    bl_description = "Add StretchTo Pose Constraints To 'ArmatureHair' "
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

        objs = context.selected_objects
        active_obj = context.active_object

        for obj in objs:
            if obj == active_obj:
                objs.remove(obj)

        objs.append(active_obj)

        if len(objs) == 2:
            if objs[0].type == 'MESH':
                if objs[1].type == 'ARMATURE':
                    self.add_poseconstraint_impl(context, objs)
                else:
                    msk_util_warning("obj[1] is not aramture")
            else:
                msk_util_warning("obj[0] is not mesh")
        else:
            msk_util_warning("select 2 objects!")

        return{'FINISHED'}

    #
    #   objs    : objs[0] MESH, objs[1] ARMATURE
    #
    def add_poseconstraint_impl(self, context, objs):
        sim_mesh = objs[0]
        armature = objs[1]


        # set 'STRETCH_TO' constraint to deform Left and Center bones
        const_name = "Damped Track"
        pose = armature.pose
        for pbone in pose.bones:
            if pbone.name.startswith("def_") and pbone.name.find(".R.") == -1:
                if not const_name in pbone.constraints:
                    pbone.constraints.new('DAMPED_TRACK')
                const = pbone.constraints[const_name]
                const.target = sim_mesh
                const.track_axis= 'TRACK_Y'
                pos = pbone.bone.tail_local + armature.location

                const.subtarget = self.get_closest_vertexgroup_name( context, pos, sim_mesh )


        # set 'STRETCH_TO' constraint to deform Right bones
        for pbone in pose.bones:
            if pbone.name.startswith("def_") and pbone.name.find(".R.") != -1:
                if not const_name in pbone.constraints:
                    pbone.constraints.new('DAMPED_TRACK')
                const = pbone.constraints[const_name]
                const.target = sim_mesh
                const.track_axis= 'TRACK_Y'

                left_pbone_name = pbone.name.replace(".R.", ".L.")
                left_pbone = pose.bones[ left_pbone_name ]
                left_const = left_pbone.constraints[ const_name ]
                subtarget_name = left_const.subtarget
                subtarget_name = subtarget_name.replace(".L", ".R")

                const.subtarget = subtarget_name



    #
    #   pos         : world coordinate
    #   sim_mesh    : mesh object
    #
    def get_closest_vertexgroup_name(self, context, pos, sim_mesh):
        mesh = sim_mesh.data
        min_len = 1000.0
        min_vg_name = ""
        vertexgroups = sim_mesh.vertex_groups

        for mvertex in mesh.vertices:
            for vge in mvertex.groups:
                if vge.group < 0 or len(vertexgroups) <= vge.group:
                    continue
                vertex_group = vertexgroups[vge.group]
                if vertex_group.name.startswith("mch_"):

                    diff = mvertex.co + sim_mesh.location - pos

                    length = diff.length

                    if length < min_len:
                        min_len = length
                        min_vg_name = vertex_group.name

        return min_vg_name


def main():
    instance = CMskAddPoseStretchToConstraint()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
