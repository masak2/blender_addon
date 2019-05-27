import bpy 
from mathutils import Color
import random
from bpy.props import *

import bmesh


class VertexGroup2VertexCol(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.vgroup2vertexcol"
    bl_label = "msk_vgroup2vertexcol"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    method=bpy.props.BoolProperty(name="Color", description="Choose the coloring method", default=False)
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        copyVertexGroup2VertexCol(context, self.method)
        context.active_object.data.update()
        return {'FINISHED'}


def copyVertexGroup2VertexCol(context, method):
    me=context.active_object
    verts=me.data.vertices
    
    col=Color()
    col.h=0
    col.s=1
    col.v=1
    
    #vcolgrp=bpy.context.active_object.data.vertex_colors.keys()
    
    try:
        assert bpy.context.active_object.vertex_groups
        assert bpy.context.active_object.data.vertex_colors
        
    except AssertionError:
        bpy.ops.error.message('INVOKE_DEFAULT', 
                type = "Error",
                message = 'you need at least one vertex group and one color group')
        return
    
    all_vgrp=bpy.context.active_object.vertex_groups
    
    vcolgrp=bpy.context.active_object.data.vertex_colors
    
    vgrp_arr = []

    for vgrp in all_vgrp:
        print (vgrp.name)
        if vgrp.name.startswith("vc_"):
            vgrp_arr.append(vgrp)


    h_offset = 40
    if len(vgrp_arr) > 9:
        h_offset = 360 / len(vgrp_arr)

    print(h_offset)

    #Check to see if we have at least one vertex group and one vertex color group
    if len(vgrp_arr) > 0 and len(vcolgrp) > 0: 
        print ("enough parameters")
        
        for i, vgrp in enumerate(vgrp_arr):
            for poly in me.data.polygons:
                for loop in poly.loop_indices:
                    vertindex=me.data.loops[loop].vertex_index        
                                           
                    #Check to see if the vertex has any geoup association
                    try:
                        weight=vgrp.weight(vertindex)
                    except:
                        continue


                    col.h=i*h_offset/255.0
                    col.s=1
                    col.v=1
                    vcolgrp.active.data[loop].color = (col.b, col.g, col.r)

        
            
        
    
class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=800, height=200)
 
    def draw(self, context):
        self.layout.label("A message has arrived")
        row = self.layout.split(0.25)
        row.prop(self, "type")
        row.prop(self, "message")
        row = self.layout.split(0.80)
        row.label("") 
        row.operator("error.ok")
 
#
#   The OK button in the error dialog
#
class OkOperator(bpy.types.Operator):
    bl_idname = "error.ok"
    bl_label = "OK"
    def execute(self, context):
        return {'FINISHED'}
    

def menu_draw(self, context): 
    self.layout.operator_context = 'INVOKE_REGION_WIN' 
    self.layout.operator(Bevel.bl_idname, "VertexGroup2VertexCol") 

def register():
    bpy.utils.register_class(VertexGroup2VertexCol)
    #bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_draw) 
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_draw) 
    
    #error window
    bpy.utils.register_class(OkOperator)
    bpy.utils.register_class(MessageOperator)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_draw) 
    bpy.utils.unregister_class(VertexGroup2VertexCol)

#if __name__ == "VertexGroup2VertexCol":
#   register()
    
def main():
    instance = VertexGroup2VertexCol()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()