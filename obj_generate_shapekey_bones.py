import bpy

#///////////////////////////////////////////////////////////////////////////////
#   
#///////////////////////////////////////////////////////////////////////////////
class MskGenerateShapeKeyBones(bpy.types.Operator):
    bl_idname = "masak.obj_generate_shapekey_bones"
    bl_label = "msk_generate_shapekey_bones"
    bl_description = "sync control bones to shapekeys"
    bl_context = "objectmode"

    ignore_keys = {"Dummy", "damy", "Basis", "m_", "vrc_", "b_", "**", "Basic"}

    kDeformPrefix = "cc_d_Driver_"
    kControlPrefix = "c_Driver_"

    kDefRootBone = "root.x"
    kCtrRootBone = "c_root.x"

    useless_driver_bones = {}

    def execute(self, context):
        print("MskGenerateShapeKeyBones")

        objs = bpy.context.selected_objects

        if len(objs) != 2:
            print("ERROR:select mesh first, select armature next")
        objArmature = bpy.context.active_object

        if objArmature.type != 'ARMATURE':
            print("ERROR:select armature last")

        objFace = None

        for obj in objs:
            if obj == objArmature:
                continue    
            objFace = obj
            
        if objFace.type != 'MESH':
            print("ERROR:select mesh first")
            
        print(objArmature.name)
        print(objFace.name)

        self.add_driver_bones(objArmature)

        self.refresh_driver_root_bones(objArmature)

        mesh = objFace.data

        key_blocks = mesh.shape_keys.key_blocks
        index = -1
        shapke_key_idx = -2
        for kb in key_blocks:
            ignore = False
            shapke_key_idx += 1
            for ignore_key in self.ignore_keys:
                if kb.name.find(ignore_key) != -1:
                    ignore = True
            if ignore:
                continue
            
            index += 1
            self.generate_driver_bones(kb, index,shapke_key_idx, objArmature)
            

        self.remove_driver_bones(objArmature)

        return{'FINISHED'}



    def add_driver_bones(self, objArmature):
        self.useless_driver_bones = set()
        armature = objArmature.data
        for b in armature.bones:
            if b.name.startswith(self.kDeformPrefix) or b.name.startswith(self.kControlPrefix):
                self.useless_driver_bones.add(b.name)

    def safe_remove_from_useless_driver_bones(self, bonename):
        if bonename in self.useless_driver_bones:
            self.useless_driver_bones.remove(bonename)

    def remove_driver_bones(self, objArmature):
        armature = objArmature.data
        bpy.ops.object.mode_set(mode='EDIT')
        for bonename in self.useless_driver_bones:
            print("REMOVE:"+bonename)
            edtibone = armature.edit_bones[bonename]
            armature.edit_bones.remove(edtibone)
        bpy.ops.object.mode_set(mode='OBJECT')

    def refresh_driver_root_bones(self, objArmature):
        armature = objArmature.data
        bpy.ops.object.mode_set(mode='EDIT')
        def_driver_root_name = self.kDeformPrefix + "Root"
        def_driver_root = self.find_or_create_bone(def_driver_root_name, armature)
        def_driver_root.head = (0.0, 0, 1.9)
        def_driver_root.tail = (0.0, 0, 1.94)
        def_driver_root.use_deform = True
        #def_driver_root.parent = self.find_or_create_bone(self.kDefRootBone, armature)
        

        ctr_driver_root_name = self.kControlPrefix + "Root"
        ctr_driver_root = self.find_or_create_bone(ctr_driver_root_name, armature)
        ctr_driver_root.head = def_driver_root.head
        ctr_driver_root.tail = def_driver_root.tail
        ctr_driver_root.use_deform = False
        #ctr_driver_root.parent = self.find_or_create_bone(self.kCtrRootBone, armature)

        self.safe_remove_from_useless_driver_bones(def_driver_root_name)
        self.safe_remove_from_useless_driver_bones(ctr_driver_root_name)
        

        bpy.ops.object.mode_set(mode='OBJECT')
        self.set_bone_layer(def_driver_root_name, 31, armature)
        self.set_bone_layer(ctr_driver_root_name, 30, armature)

    def generate_driver_bones(self, key_block, index, shapke_key_idx, objArmature):
        armature = objArmature.data
        suffix = "0"# str(shapke_key_idx).zfill(3) to avoid id missing
        def_bone_name = self.kDeformPrefix + key_block.name + suffix # to avoid x axis mirror
        ctr_bone_name = self.kControlPrefix + key_block.name + suffix

        
                
        bpy.ops.object.mode_set(mode='EDIT')
        def_bone = self.find_or_create_bone(def_bone_name, armature)
        ctr_bone = self.find_or_create_bone(ctr_bone_name, armature)

        self.safe_remove_from_useless_driver_bones(def_bone_name)
        self.safe_remove_from_useless_driver_bones(ctr_bone_name)
       
        x = index // 20
        z = index % 20

        
        def_bone.head = [x * 0.25, 0, 2.0 + z * 0.05]
        def_bone.tail = [def_bone.head.x, 0, def_bone.head.z + 0.03]
        def_bone.roll = 0.0
        def_bone.parent = armature.edit_bones[self.kDeformPrefix+"Root"]
        def_bone.use_deform = True

        head = def_bone.head
        ctr_bone.head = [head.x, head.y, head.z]
        tail = def_bone.tail
        ctr_bone.tail = [tail.x, tail.y, tail.z]
        ctr_bone.roll = def_bone.roll
        ctr_bone.parent = armature.edit_bones[self.kControlPrefix+"Root"]
        ctr_bone.use_deform = False
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.set_bone_layer(def_bone_name, 31, armature)
        self.set_bone_layer(ctr_bone_name, 16, armature)
        
        
        bpy.ops.object.mode_set(mode='POSE')
        self.setup_pose_deform_bone(def_bone_name, ctr_bone_name, objArmature)
        self.setup_pose_control_bone(ctr_bone_name, objArmature)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.setup_driver(key_block, ctr_bone_name, objArmature)
        self.setup_curve_text(key_block, ctr_bone_name, objArmature)

    def setup_pose_deform_bone(self, def_bone_name,ctr_bone_name, objArmature):
        pose_def = objArmature.pose.bones[def_bone_name]
        const = self.find_or_create_constraint(pose_def, 'Copy Transforms', "COPY_TRANSFORMS")
        const.target = objArmature
        const.subtarget = ctr_bone_name

    def setup_pose_control_bone(self, ctr_bone_name, objArmature):
        
        
        pose_ctr = objArmature.pose.bones[ctr_bone_name]
        pose_ctr.lock_location[1] = True
        pose_ctr.lock_location[2] = True
        pose_ctr.lock_rotation_w = True
        pose_ctr.lock_rotation[0] = True
        pose_ctr.lock_rotation[1] = True
        pose_ctr.lock_rotation[2] = True
        pose_ctr.lock_scale[0] = True
        pose_ctr.lock_scale[1] = True
        pose_ctr.lock_scale[2] = True
        const = self.find_or_create_constraint(pose_ctr,'Limit Location','LIMIT_LOCATION')
        const.min_x = 0.0
        const.max_x = 0.1
        const.use_min_x = True
        const.use_max_x = True
        const.use_transform_limit = True
        const.owner_space = 'LOCAL'
        

    def setup_driver(self, kb, ctr_bone_name, objArmature):
        driver = kb.driver_add('value')
        driver.driver.type = 'AVERAGE'
        
        varidx = driver.driver.variables.find("var")
        
        if varidx == -1:
            varnew = driver.driver.variables.new()
            varnew.name = "var"
        var = driver.driver.variables["var"]
        var.type = 'TRANSFORMS'
        #var.targets[0].id_type = 'ARMATURE'
        target = var.targets[0]
        target.id = objArmature
        target.bone_target = ctr_bone_name
        target.transform_space = 'LOCAL_SPACE'
        target.transform_type = 'LOC_X'
            
        if len(driver.modifiers) == 0:
            mnew = driver.modifiers.new('GENERATOR')
        
        modi = driver.modifiers[0]
        modi.active = True
        modi.mode = 'POLYNOMIAL'
        modi.poly_order = 1
        modi.coefficients[0] = 0
        modi.coefficients[1] = 10

        

    def setup_curve_text(self, key_block, ctr_bone_name, objArmature):
        if bpy.data.curves.find(ctr_bone_name) == -1:
            text = bpy.data.curves.new(ctr_bone_name, 'FONT')
        text = bpy.data.curves[ctr_bone_name]
        text.size = 0.03
        text.body = key_block.name
        fontidx = bpy.data.fonts.find("Yu Gothic Regular")
        text.font = bpy.data.fonts[fontidx]

        if bpy.data.objects.find(ctr_bone_name)==-1:
            bpy.data.objects.new(ctr_bone_name, text)
        objText = bpy.data.objects[ctr_bone_name]

        print( objText.name)
        #objText.hide_select = True
        const = self.find_or_create_constraint(objText, 'Copy Transforms', 'COPY_TRANSFORMS')
        const.target = objArmature
        const.subtarget = ctr_bone_name
        
        if bpy.data.collections.find("ShapeKeyText")==-1:
            new_coll = bpy.data.collections.new("ShapeKeyText")
            bpy.context.scene.collection.children.link(new_coll) #add new coll to the scene
            
        collection = bpy.data.collections["ShapeKeyText"]
        if collection.objects.find(ctr_bone_name) == -1:
            collection.objects.link(objText)

    def merge_curve_text(self, key_block):
        return


        
    def find_or_create_bone(self, bone_name, armature):
        if armature.edit_bones.find(bone_name) != -1:
            return armature.edit_bones[bone_name]
        else:
            bone = armature.edit_bones.new(name=bone_name)
            return bone



    def set_bone_layer(self, bone_name, idx, armature):
        armature.bones[bone_name].layers[idx] = True
        for i in range(32):
            if i == idx:
                continue
            armature.bones[bone_name].layers[i] = False


    def find_or_create_constraint(self, target, constraint_name, constraint_type):
        idx_constraint = target.constraints.find(constraint_name)
        if idx_constraint == -1:
            target.constraints.new(constraint_type)
        return target.constraints[constraint_name]