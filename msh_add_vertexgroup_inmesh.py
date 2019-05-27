#-------------------------------------------------------------------------------
# Name:        msh_add_vertexgroup_inmesh
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
from masak.util_various import *

#breakpoint = bpy.types.bp.bp

class CMskAddVertexGroupInMesh(bpy.types.Operator):
##class CMskAddVertexGroupInMesh():
    bl_idname = "masak.msk_add_vertexgroup_inmesh"
    bl_label = "msk_add_vertexgroup_inmesh"
    bl_description = "Add vertex groups to vertices in 'vgset' vertex group "
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                self.add_vertexgroup_impl(context, obj)

        return{'FINISHED'}


    def add_vertexgroup_impl(self, context, obj):

        # check if obj has mirror modifier
        if not "Mirror" in obj.modifiers:
            return


        # get the 'vgset' vertexgroup's Index
        vg_index = -1
        for vg in obj.vertex_groups:
            if vg.name == "vgset":
                vg_index = vg.index
                break
        if vg_index == -1:
            return


        # get vertex index list which are included in 'vgset' vertex group
        index_list = []
        mesh = obj.data
        for meshvertex in mesh.vertices:
            for vge in meshvertex.groups:
                if vge.group == vg_index:
                    index_list.append( meshvertex.index )

        if len(index_list) == 0:
            return


        # delete vertex groups which are not needed
        exceptname_list = ["pin", "vgset"]
        self.delete_allvertexgroup_except( context, obj, exceptname_list )


        # add vertex group
        for vertex_index in index_list:
            meshvertex = mesh.vertices[ vertex_index ]
            vgname_base = "mch_" + ( "%03d" % vertex_index )
            vertex_group = None

            if meshvertex.co.x == 0.0:
                obj.vertex_groups.new(vgname_base)
                vertex_group = obj.vertex_groups[vgname_base]
            else:
                obj.vertex_groups.new(vgname_base + ".L")
                obj.vertex_groups.new(vgname_base + ".R")

                vertex_group = obj.vertex_groups[vgname_base + ".L"]

            vertex_group.add([vertex_index], 1.0, 'ADD')



    def delete_allvertexgroup_except(self, context, obj, exceptname_list):
        for vg in obj.vertex_groups:
            except_vg = False
            for name in exceptname_list:
                if vg.name == name:
                    except_vg = True
                    break
            if except_vg:
                continue

            obj.vertex_groups.remove( vg )

def main():
    instance = CMskAddVertexGroupInMesh()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
