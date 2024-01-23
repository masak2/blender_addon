import bpy

#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskGenerateCtrBonesSelected(bpy.types.Operator):
    bl_idname = "masak.msk_gen_ctr_bones_selected"
    bl_label = "msk_gen_ctr_bones_selected"
    bl_description = "Create controll bones for selected bones"

    def execute(self, context):
        print("MskGenerateCtrBones")
        obj = bpy.context.object
        armobj = obj.data
        

        selected_bonenames = []
        for bone in armobj.bones:
            if bone.select:
                selected_bonenames.append(bone.name)
                #print(bone.name)
        new_bonename_arr = []
        for bonename in selected_bonenames:
            ctr_bone_name = self.get_ctr_bonename(bonename)
            if False == self.exists(armobj.bones, ctr_bone_name):
                new_bonename_arr.append(ctr_bone_name)
        

        bpy.ops.object.mode_set(mode='EDIT')
        for bonename in new_bonename_arr:
            bone = armobj.edit_bones.new('Bone')
            bone.name = bonename
            #print(bonename)

        #tweak
        for bonename in selected_bonenames:
            def_bone = self.find_bone(armobj.edit_bones, bonename)
            ctr_bone_name = self.get_ctr_bonename(bonename)
            ctr_bone = self.find_bone(armobj.edit_bones, ctr_bone_name)
            ctr_bone.head = def_bone.head
            ctr_bone.tail = def_bone.tail
            ctr_bone.roll = def_bone.roll
            ctr_bone.use_deform = False

            if def_bone.parent != None:
                exist = ctr_bone.get("not_parent_auto", 0.0)
                if exist == 0.0:
                    parent_bone_name = self.get_ctr_bonename(def_bone.parent.name)
                    ctr_bone.parent = self.find_bone(armobj.edit_bones, parent_bone_name)
            else:
                ctr_bone.parent = None
        
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='POSE')
       
        for bonename in selected_bonenames:

            bpy.ops.pose.select_all(action='DESELECT')
            posebone = self.find_bone(obj.pose.bones, bonename)
            #print(bonename)
            armobj.bones.active = posebone.bone

            idx = posebone.constraints.find('Copy Transforms')
            if idx == -1:
                posebone.constraints.new('COPY_TRANSFORMS')

                #bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')

            const = posebone.constraints['Copy Transforms']

            const.target = obj
            const.subtarget = self.get_ctr_bonename(posebone.name)
                

        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}
        
    def isDeformBone(self, bonename):
        for key in defBoneKeywords:
            if bonename.startswith(key):
                return True

        for specialBone in specialBones:
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
        return "c_" + def_bonename


