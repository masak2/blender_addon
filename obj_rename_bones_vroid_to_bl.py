import bpy

#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskRenameBonesVroidToBL(bpy.types.Operator):
    bl_idname = "masak.obj_rename_bones_vroid_to_bl"
    bl_label = "msk_rename_bones_vroid_to_bl"
    bl_description = "Rename vroid bones to blender style"
    bl_context = "objectmode"

    def execute(self, context):
        print("MskRenameVroidToBL")
        obj = bpy.context.object
        armobj = obj.data

        keys = ["J_Bip_L", "J_Bip_R", "Ctr_J_Bip_L", "Ctr_J_Bip_R","J_Sec_L","J_Sec_R","Ctr_J_Sec_L","Ctr_J_Sec_R"]

        for bone in armobj.bones:
            bonename = bone.name
            print(bonename)
            parts = bonename.split("_")
            last = parts[len(parts)-1]

            for key in keys:
                if bonename.startswith(key) and bonename.find(".") == -1:
                    first = key[0:len(key)-1]
                    suffix = key[-2:0]
                    bone.name = first + last + suffix


        return{'FINISHED'}

        