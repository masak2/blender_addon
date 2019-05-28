import bpy
import mathutils
import math
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
    pole_angle = {}

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

        self.pole_angle["legL"] = self.findBoneByKeyword("legL").get("pole_angle", 0.0)
        self.pole_angle["legR"] = self.findBoneByKeyword("legR").get("pole_angle", 0.0)
        self.createBonesIfNone("L")
        self.createBonesIfNone("R")
        

        # ik
        self.tweakEditBones("L")
        self.tweakEditBones("R")

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='POSE')
        self.addConstraintsIfNeed("L")
        self.addConstraintsIfNeed("R")
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
        targetBone.head[1] += 0.1
        targetBone.tail = targetBone.head
        targetBone.tail[1] += 0.1
        targetBone.use_deform = False
        targetBone.parent = self.findBone("ik_foot_"+postfix)

    def addConstraintsIfNeed(self, postfix):
        obj = bpy.context.object
        # IK
        posebone = self.findPoseBoneByKeyword("leg" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'IK')
        const.target = obj
        const.subtarget = "ik_foot_"+postfix
        const.pole_target = obj
        const.pole_subtarget = "pole_knee_"+postfix
        const.chain_count = 2
        const.pole_angle =  self.pole_angle["leg" + postfix] / 180.0 * math.pi
        posebone.lock_ik_y = True
        posebone.lock_ik_z = True


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

    def safeSelectPoseBone(self, posebone):
        bpy.ops.pose.select_all(action='DESELECT')

        
        self.armobj.bones.active = posebone.bone

    def safeFindConstraint(self, posebone, key):
        idx = posebone.constraints.find(key)
        if idx == -1:
            bpy.ops.pose.constraint_add(type=key)

        return posebone.constraints[key]

    def findPoseBone(self, bonename):
        for bone in bpy.context.object.pose.bones:
            if bone.name == bonename:
                return bone
            
        print("no pose bone=" + bonename)
        return None
    def findPoseBoneByKeyword(self, keyword):
        bonename = self.legRelatedBoneTable[keyword]
        return self.findPoseBone(bonename)
