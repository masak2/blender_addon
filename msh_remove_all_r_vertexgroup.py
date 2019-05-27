#-------------------------------------------------------------------------------
# Name:        msh_remove_all_r_vertexgroup
# Purpose:
#
# Author:      masak
#
# Created:     25/02/2012
# Copyright:   (c) masak 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import bpy
from masak.util_various import *

#breakpoint = bpy.types.bp.bp

class CMskRemoveAllRVertexGroup(bpy.types.Operator):
##class CMskRemoveAllRVertexGroup():
    bl_idname = "masak.msk_remove_all_r_vertexgroup"
    bl_label = "msk_remove_all_r_vertexgroup"
    bl_description = "Delete All R vertex group"
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

        # delete vertex groups whose name contains '_R' '.R' '_R.???' '.R.???'
        for vg in obj.vertex_groups:
            bRemove = self.ismirrorable_vertex_group('R', vg.name)
            if bRemove:
                obj.vertex_groups.remove( vg)

    def ismirrorable_vertex_group(self, char, vgname):

        bRemove = False
        if vgname.endswith('_' + char):
            bRemove = True
        elif vgname.endswith('.' + char):
            bRemove = True

        if(bRemove == False):
            vgname_len = len(vgname)
            #print( vgname_len )
            tmpDigit = vgname[vgname_len - 3: 3]
            if( tmpDigit.isdigit ):
                tmpvgname = vgname[0:vgname_len-4]
                if tmpvgname.endswith('_' + char):
                    bRemove = True
                elif tmpvgname.endswith('.' + char):
                    bRemove = True

        return bRemove

def main():
    instance = CMskRemoveAllRVertexGroup()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
