import bpy
import bpy.ops
from masak.util_count_bone import *

class VIEW3D_tools_varioushelper(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "VariousHelper"
    bl_context = "objectmode"



    def draw(self, context):
        layout = self.layout
        column = layout.column()
##        column.label("hello world10")
        column.prop(context.scene, "hair_front_total")
        column.prop(context.scene, "hair_side_total")
        column.prop(context.scene, "hair_back0_total")
        column.prop(context.scene, "hair_back1_total")
        column.separator()
        column.operator("masak.msk_util_count_bone", text="CountBone")
        column.label("bone total = " + str(context.scene.bone_total))
        column.label("defbone total = " + str(context.scene.deform_bone_total))
        column.prop(context.scene, "arm_switch_layer")
        column.operator("masak.msk_export_project_fbx", text="ExportFbx")