import bpy
import mathutils
#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskGenerateLegRig(bpy.types.Operator):
    bl_idname = "masak.msk_gen_leg_rig"
    bl_label = "msk_gen_leg_rig"
    bl_description = "Create leg rigs automatically"
    bl_context = "objectmode"

    legRigBoneNames = ["ik_foot_","pole_knee_", "mch_foot_", "mch_toe_", "mch_ball_", "mch_heel_", "ctr_roll_"]
    legRelatedBoneTable = {}
    armobj = None

    def execute(self, context):
        print("MskGenerateLegRig")
        obj = bpy.context.object
        self.armobj = obj.data


        for bone in self.armobj.bones:
            value = bone.get("rig_info", "none")
            if value != "none":
                self.legRelatedBoneTable[value] = bone.name
                print(value + "=" + bone.name)
            
        bpy.ops.object.mode_set(mode='EDIT')
        self.createBonesIfNone("L")
        self.createBonesIfNone("R")
        

        # ik
        self.tweakEditBones("L")
        self.tweakEditBones("R")
        return{'FINISHED'}
        #tweak
        for def_bone in self.armobj.edit_bones:
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

    def createBonesIfNone(self, postfix):
        for bonename in self.legRigBoneNames:
            bonename = bonename + postfix
            if self.existsBone(bonename):
                continue

            bone = self.armobj.edit_bones.new('Bone')
            bone.name = bonename
            print("new " + bonename)

    def tweakEditBones(self, postfix):
        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("ik_foot_"+postfix)
        targetBone.head = srcBone.head
        targetBone.tail = srcBone.head
        targetBone.tail[2] += -0.2
        targetBone.use_deform = False
        targetBone.parent = self.findBoneByKeyword("root")

        srcBone = self.findBoneByKeyword("leg"+postfix)
        targetBone = self.findBone("pole_knee_"+postfix)
        targetBone.head = srcBone.head
        targetBone.head[1] += -0.4
        targetBone.tail = srcBone.head
        targetBone.tail[1] += -0.5
        targetBone.use_deform = False
        targetBone.parent = self.findBoneByKeyword("root")

        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("mch_foot_"+postfix)
        targetBone.head = srcBone.head
        targetBone.tail = srcBone.tail
        targetBone.use_deform = False
        targetBone.parent = self.findBone("mch_ball_"+postfix)

        srcBone = self.findBoneByKeyword("toe"+postfix)
        targetBone = self.findBone("mch_toe_"+postfix)
        targetBone.head = srcBone.head
        targetBone.tail = srcBone.tail
        targetBone.use_deform = False
        targetBone.parent = self.findBone("mch_heel_"+postfix)

        
        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("mch_heel_"+postfix)
        vecA = mathutils.Vector((0,0,srcBone.tail[2]-srcBone.head[2]))
        legBone = self.findBoneByKeyword("leg"+postfix)
        vecN = mathutils.Vector(legBone.tail) - mathutils.Vector(legBone.head)
        print(vecA.length)
        vecN.normalize()
        coef = vecA.length * vecA.length / vecA.dot(vecN)
        vecX = coef * vecN
        print(vecX)
        vecHeel = mathutils.Vector(srcBone.head) + vecX
        targetBone.head = vecHeel
        targetBone.tail = vecHeel + (mathutils.Vector( srcBone.tail) - vecHeel) / 2
        targetBone.use_deform = False
        targetBone.parent = self.findBone("ik_foot_"+postfix)

        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("mch_ball_"+postfix)
        targetBone.head = srcBone.tail
        targetBone.tail = vecHeel + (mathutils.Vector( srcBone.tail) - vecHeel) / 2
        targetBone.use_deform = False
        targetBone.parent = self.findBone("mch_heel_"+postfix)


        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("ctr_roll_"+postfix)
        targetBone.head = srcBone.head
        targetBone.head[1] + 0.1
        targetBone.tail = targetBone.head
        targetBone.tail[1] += 0.1
        targetBone.use_deform = False
        targetBone.parent = self.findBone("ik_foot_"+postfix)


    def existsBone(self, bonename):
        for bone in self.armobj.bones:
            if bone.name == bonename:
                return True
        return False
    def findBone(self, bonename):
        for bone in self.armobj.edit_bones:
            if bone.name == bonename:
                return bone
            
        print("no bone=" + bonename)
        return None
    def findBoneByKeyword(self, keyword):
        bonename = self.legRelatedBoneTable[keyword]
        return self.findBone(bonename)

