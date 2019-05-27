import bpy

class test2(bpy.types.Operator):
    bl_idname = "masak.test2"
    bl_label = "test2"
    bl_description = "Create a Cloud,Undo Cloud, or convert to Mesh Cloud depending on selection"

    def execute(self, context):
        print("aaa")
        return{"FINISHED"}