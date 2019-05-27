import bpy

#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskGenerateCtrBones(bpy.types.Operator):
    bl_idname = "masak.msk_gen_ctr_bones"
    bl_label = "msk_gen_ctr_bones"
    bl_description = "Create controll bones"
    bl_context = "objectmode"

    specialBones = ["Root", "Position", "Global"]
    defBoneKeywords = ["J_", "HairJoint"]

    def execute(self, context):
        print("MskGenerateCtrBones")
        obj = bpy.context.object
        armobj = obj.data

        new_bonename_arr = []
        for bone in armobj.bones:
            if self.isDeformBone(bone.name):
                
                ctr_bone_name = self.get_ctr_bonename(bone.name)
                if False == self.exists(armobj.bones, ctr_bone_name):
                    new_bonename_arr.append(ctr_bone_name)
        

        bpy.ops.object.mode_set(mode='EDIT')
        for bonename in new_bonename_arr:
            bone = armobj.edit_bones.new('Bone')
            bone.name = bonename
            print(bonename)

        #tweak
        for def_bone in armobj.edit_bones:
            if self.isDeformBone(def_bone.name):
                ctr_bone_name = self.get_ctr_bonename(def_bone.name)
                ctr_bone = self.find_bone(armobj.edit_bones, ctr_bone_name)
                ctr_bone.head = def_bone.head
                ctr_bone.tail = def_bone.tail
                ctr_bone.roll = def_bone.roll
                ctr_bone.use_deform = False

                if def_bone.parent != None:
                    parent_bone_name = self.get_ctr_bonename(def_bone.parent.name)
                    ctr_bone.parent = self.find_bone(armobj.edit_bones, parent_bone_name)
                else:
                    ctr_bone.parent = None
        
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='POSE')
        for posebone in obj.pose.bones:
            if self.isDeformBone(posebone.name):

                bpy.ops.pose.select_all(action='DESELECT')
                armobj.bones.active = posebone.bone

                idx = posebone.constraints.find('Copy Transforms')
                if idx == -1:
                    bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')

                const = posebone.constraints['Copy Transforms']

                const.target = obj
                const.subtarget = self.get_ctr_bonename(posebone.name)
                

        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}
        
    def isDeformBone(self, bonename):
        for key in self.defBoneKeywords:
            if bonename.startswith(key):
                return True

        for specialBone in self.specialBones:
            if bonename == specialBone:
                return True

        return False

    def exists(self, bones, bone_name):
        for bone in bones:
            if bone.name == bone_name:
                return True
        return False
    def find_bone(self, bones, bone_name):
        for bone in bones:
            if bone.name == bone_name:
                return bone
        return None
    def get_ctr_bonename(self, def_bonename):
        return "Ctr_" + def_bonename