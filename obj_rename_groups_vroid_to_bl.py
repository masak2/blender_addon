import bpy

#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskRenameGroupsVroidToBL(bpy.types.Operator):
    bl_idname = "masak.obj_rename_groups_vroid_to_bl"
    bl_label = "msk_rename_groups_vroid_to_bl"
    bl_description = "Rename vroid vertex groups to blender style"
    bl_context = "objectmode"

    def execute(self, context):
        print("MskRenameGroupsVroidToBL")
        obj = bpy.context.object
        mesh = obj.data
        vg = obj.vertex_groups

        keys = ["J_Bip_L", "J_Bip_R","J_Sec_L","J_Sec_R"]

        for vgi in vg:
            print(vgi.name)
            vginame = vgi.name
            parts = vginame.split("_")
            last = parts[len(parts)-1]
            for key in keys:
                if vginame.startswith(key) and vginame.find(".") == -1:
                    first = key[0:len(key)-1]
                    suffix = key[-2:]
                    print(first)
                    print(last)
                    print(suffix)
                    vgi.name = first + last + suffix
                    break

        return{'FINISHED'}

        