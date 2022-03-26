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
        self.setLayer(targetBone, 0)

        srcBone = self.findBoneByKeyword("leg"+postfix)
        targetBone = self.findBone("pole_knee_"+postfix)
        targetBone.head = srcBone.head
        targetBone.head[1] += -0.4
        targetBone.tail = srcBone.head
        targetBone.tail[1] += -0.5
        targetBone.use_deform = False
        targetBone.parent = self.findBoneByKeyword("root")
        self.setLayer(targetBone, 0)

        srcBone = self.findBoneByKeyword("foot"+postfix)
        targetBone = self.findBone("mch_foot_"+postfix)
        targetBone.head = srcBone.head
        targetBone.tail = srcBone.tail
        targetBone.roll = srcBone.roll
        targetBone.use_deform = False
        targetBone.parent = self.findBone("mch_ball_"+postfix)

        srcBone = self.findBoneByKeyword("toe"+postfix)
        targetBone = self.findBone("mch_toe_"+postfix)
        targetBone.head = srcBone.head
        targetBone.tail = srcBone.tail
        targetBone.roll = srcBone.roll
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
        self.setLayer(targetBone, 0)

    def addConstraintsIfNeed(self, postfix):
        obj = bpy.context.object
        # IK
        posebone = self.findPoseBoneByKeyword("leg" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'IK', "IK")
        const.target = obj
        const.subtarget = "mch_foot_"+postfix
        const.pole_target = obj
        const.pole_subtarget = "pole_knee_"+postfix
        const.chain_count = 2
        const.pole_angle =  self.pole_angle["leg" + postfix] / 180.0 * math.pi
        posebone.lock_ik_y = True
        posebone.lock_ik_z = True

        # ctr foot
        posebone = self.findPoseBoneByKeyword("foot" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'COPY_TRANSFORMS', "Copy Transforms")
        const.target = obj
        const.subtarget = "mch_foot_" + postfix
        # Space はworld worldになってるはず

        # ctr toe
        posebone = self.findPoseBoneByKeyword("toe" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'COPY_TRANSFORMS', "Copy Transforms")
        const.target = obj
        const.subtarget = "mch_toe_" + postfix
        # Space はworld worldになってるはず

        # mch ball
        posebone = self.findPoseBone("mch_ball_" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'COPY_ROTATION', "Copy Rotation")
        const.target = obj
        const.subtarget = "ctr_roll_" + postfix
        const.use_x = True
        const.use_y = False
        const.use_z = False
        const.target_space = 'LOCAL'
        const.owner_space =  'LOCAL'
        const = self.safeFindConstraint(posebone, 'LIMIT_ROTATION', "Limit Rotation")
        const.use_limit_x = True
        const.use_limit_y = False
        const.use_limit_z = False
        const.min_x = 0
        const.max_x = self.convertRadian(90)
        const.owner_space =  'LOCAL'

        # mch heel
        posebone = self.findPoseBone("mch_heel_" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone,'COPY_ROTATION', "Copy Rotation")
        const.target = obj
        const.subtarget = "ctr_roll_" + postfix
        const.use_x = True
        const.use_y = True
        const.use_z = True
        const.invert_x = True
        const.target_space = 'LOCAL'
        const.owner_space =  'LOCAL'
        const = self.safeFindConstraint(posebone, 'LIMIT_ROTATION', "Limit Rotation")
        const.use_limit_x = True
        const.use_limit_y = False
        const.use_limit_z = False
        const.min_x = 0
        const.max_x = self.convertRadian(90)
        const.use_transform_limit = True
        const.owner_space =  'LOCAL'

        # ctr roll
        posebone = self.findPoseBone("ctr_roll_" + postfix)
        self.safeSelectPoseBone(posebone)
        const = self.safeFindConstraint(posebone, 'LIMIT_ROTATION', "Limit Rotation")
        const.use_limit_x = True
        const.use_limit_y = True
        const.use_limit_z = True
        const.min_x = self.convertRadian(-30)
        const.max_x = self.convertRadian(60)
        # 他のmin maxはdefault 0
        const.owner_space =  'LOCAL'

    # もしかしたら将来的に指定idにのみ存在させるかも
    def setLayer(self, editBone, id):
        editBone.layers[id] = True

    def convertRadian(self, angle):
        return angle / 180.0 * math.pi

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
        # error文を
        if not keyword in self.legRelatedBoneTable:
            print("no rig_info value=" + keyword)

        bonename = self.legRelatedBoneTable[keyword]
        return self.findBone(bonename)

    def safeSelectPoseBone(self, posebone):
        bpy.ops.pose.select_all(action='DESELECT')

        
        self.armobj.bones.active = posebone.bone

    def safeFindConstraint(self, posebone, key, constname):
        idx = posebone.constraints.find(constname)
        if idx == -1:
            bpy.ops.pose.constraint_add(type=key)

        return posebone.constraints[constname]

    def findPoseBone(self, bonename):
        for bone in bpy.context.object.pose.bones:
            if bone.name == bonename:
                return bone
            
        print("no pose bone=" + bonename)
        return None
    def findPoseBoneByKeyword(self, keyword):
        bonename = self.legRelatedBoneTable[keyword]
        return self.findPoseBone(bonename)
