import bpy

#///////////////////////////////////////////////////////////////////////////////
#   make armature for cloth sim
#///////////////////////////////////////////////////////////////////////////////
class CMskGenerateSkirtBone(bpy.types.Operator):
    bl_idname = "masak.msk_gen_skirt_armature"
    bl_label = "msk_gen_skirt_armature"
    bl_description = "Create Skirt Rig for cloth sim"
    bl_context = "objectmode"

    def execute(self, context):

        obj = bpy.context.object
        mesh = obj.data

        tmp = []
        for i,x in enumerate(obj.vertex_groups):
            name = x.name.split('.')
            if len(name) != 2:
                continue
            tmp.append([int(name[0]),int(name[1]),x])

        c_x = 0
        c_y = 0
        for x in tmp:
            if x[0] > c_x:
                c_x = x[0]
            if x[1] > c_y:
                c_y = x[1]

        c_x += 1
        c_y += 1

        vgs = []
        for i in range(c_x):
            l = []
            for j in range(c_y):
                l.append(None)
            vgs.append(l)

        for x in tmp:
            #print(c_y,x)
            vgs[x[0]][x[1]] = x[2]

        bpy.ops.object.armature_add(enter_editmode=True)
        bpy.ops.armature.select_all()

        bone = bpy.context.selected_bones[0]
        bone.name = 'Center'
        center_bone = bone

        for i in range(c_x):
            bpy.ops.armature.duplicate()
            bone = bpy.context.selected_bones[0]
            bone.name = str(i) +'.1'

            bone.head = self.vg_loc(mesh, vgs[i][0])
            bone.tail = self.vg_loc(mesh, vgs[i][1])
            bone.parent = center_bone

            for j in range(c_y-2):
                bpy.ops.armature.extrude()
                bone = bpy.context.active_bone
                bone.name = str(i) +'.'+str(j+2)
                bone.head = self.vg_loc(mesh, vgs[i][j+1])
                bone.tail = self.vg_loc(mesh, vgs[i][j+2])

            bpy.ops.armature.select_all(action='DESELECT')
            center_bone.select = True
            center_bone.select_head = True
            center_bone.select_tail = True

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.object.location = obj.location

        bpy.ops.object.mode_set(mode='POSE')
        armobj = bpy.context.object

        for x in armobj.pose.bones:
            if x.name == 'Center':
                continue
            bpy.ops.pose.select_all(action='DESELECT')
            armobj.data.bones.active = x.bone
            bpy.ops.pose.constraint_add(type='STRETCH_TO')

            const = x.constraints['Stretch To']

            const.target = obj
            const.subtarget = x.name
            bpy.ops.constraint.stretchto_reset(constraint="Stretch To", owner='BONE')

        bpy.ops.object.mode_set(mode='OBJECT')

        return{'FINISHED'}



    def mtx_plus(self, mtx1, mtx2):
        ret = [0.0,0.0,0.0]
        for i,x in enumerate(mtx1):
            ret[i] = x + mtx2[i]
        return ret

    def mtx_div(self, mtx1, val):
        ret = [0.0,0.0,0.0]
        for i,x in enumerate(mtx1):
            ret[i] = x / val
        return ret

    def vg_loc(self, mesh, vg):
        ret = [0.0,0.0,0.0]

        ws = 0.0
        for x in mesh.vertices:
            for y in x.groups:
                if y.group == vg.index:
                    ws += y.weight
                    ret = self.mtx_plus(ret, x.co*y.weight)

        ret = self.mtx_div(ret, ws)

        return ret
