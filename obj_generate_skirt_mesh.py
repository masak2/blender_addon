import bpy

#///////////////////////////////////////////////////////////////////////////////
#   make a pleats skirt
#///////////////////////////////////////////////////////////////////////////////
class CBaseMskGenerateSkirtMesh:
    class CSettings:
        def __init__(self):
            self.width = 0.0
            self.hight = 0.0
            self.length= 0.0
            self.count = 1     #counts of parts
            self.vg_count = 1   #number of vertex group
            self.vt_cd = [[-0.1,0]]   #[x,y] of parts (0.0-1.0)

            self.vt_gr = [[[-1,0.5],[0,0.5]]]

            self.divy = 0

    def __init__(self):
        self.m_settings = self.CSettings()

    def execute(self, context):
        print("CBaseMskGenerateSkirtMesh called")

        mesh = bpy.data.meshes.new("Skirt.Sim")
        obj = bpy.data.objects.new("Skirt.Sim", mesh)
        bpy.context.scene.objects.link(obj)

        ve=[]
        ed=[]
        fa=[]

        topz = self.m_settings.hight
        lowz = self.m_settings.hight - self.m_settings.length
        partlen = self.m_settings.width/self.m_settings.count

        vtc_p = len(self.m_settings.vt_cd)
        if vtc_p != len(self.m_settings.vt_gr):
            print('errer:vertex settings wrong')

        step_z = lowz/(self.m_settings.divy+1)
        count_y = 2+self.m_settings.divy

        curx = 0

        for i in range(self.m_settings.count):
            for j in self.m_settings.vt_cd:
                z = topz
                for k in range(count_y):
                    ve.append((j[0]*partlen+curx,j[1]*partlen,z))
                    z -= step_z
            curx += partlen



        for i in range(self.m_settings.count*vtc_p-1):
            base = i*count_y
            for j in range(count_y-1):
                fa.append((base+count_y+j, base+count_y+j+1, base+j+1, base+j))

        '''
        t = [1,2]
        print(t[3])
        '''
        mesh.from_pydata(ve,ed,fa)
        mesh.update(calc_edges=True)



        tmp = 0
        vgs = []
        tvgs = []
        for i in range(self.m_settings.count):
            for j in range(self.m_settings.vg_count):
                for k in range(count_y):
                    vgname = str(tmp)+'.'+str(k)
                    tvgs.append(obj.vertex_groups.new(vgname))
                vgs.append(tvgs)
                tvgs = []
                tmp += 1

        tmp = 0
        index = 0
        for i in range(self.m_settings.count):
            for j in self.m_settings.vt_gr:
                for k in range(count_y):
                    for x in j:
                        num = x[0]+tmp
                        if num < 0:
                            num += self.m_settings.vg_count*self.m_settings.count
                        if num >= self.m_settings.vg_count*self.m_settings.count:
                            num = x[0] - self.m_settings.vg_count
                        vgs[num][k].add(index=[index],weight=x[1],type='ADD')
                    index += 1

            tmp += self.m_settings.vg_count
        return {'FINISHED'}



#///////////////////////////////////////////////////////////////////////////////
#   make a pleats skirt for cloth simulation
#///////////////////////////////////////////////////////////////////////////////
class CMskGenerateSkirtSimMesh(bpy.types.Operator, CBaseMskGenerateSkirtMesh):
    bl_idname = "masak.msk_gen_skirt_sim_mesh"
    bl_label = "msk_gen_skirt_sim_mesh"
    bl_description = "Create Skirt Mesh for cloth sim"

    def execute(self, context):
        self.m_settings.width = 1.0
        self.m_settings.hight = 1.0
        self.m_settings.length= 0.45
        self.m_settings.count = 8     #counts of parts
        self.m_settings.vg_count = 2   #number of vertex group
        self.m_settings.vt_cd = [[-0.1,0],[-0.4,-0.3],[0.4,-0.3],[0.1,0]]   #[x,y] of parts (0.0-1.0)

        self.m_settings.vt_gr = [[[-1,0.5],[0,0.5]],[],[],[[0,0.5],[1,0.5]]]

        self.m_settings.divy = 2

        print("CMskGenerateSkirtSimMesh called")
        CBaseMskGenerateSkirtMesh.execute(self, context)

        return{"FINISHED"}



#///////////////////////////////////////////////////////////////////////////////
#   make a pleats skirt for common deform mesh
#///////////////////////////////////////////////////////////////////////////////
class CMskGenerateSkirtDefMesh(bpy.types.Operator, CBaseMskGenerateSkirtMesh):
    bl_idname = "masak.msk_gen_skirt_def_mesh"
    bl_label = "msk_gen_skirt_def_mesh"
    bl_description = "Create Skirt Mesh for deform"

    def execute(self, context):
        self.m_settings.width = 1.0
        self.m_settings.hight = 1.0
        self.m_settings.length= 0.45
        self.m_settings.count = 16     #counts of parts
        self.m_settings.vg_count = 1   #number of vertex group
        self.m_settings.vt_cd = [[0,0],[-0.02667,-0.05333],[-0.1733,-0.3467],[-0.2,-0.4],[-0.14,-0.38],[0.4,-0.2],[0.94,-0.02]]   #[x,y] of parts (0.0-1.0)

        self.m_settings.vt_gr = [[[0,1]],[[0,0.9],[1,0.1]],[[0,0.35],[1,0.65]],[[0,0.3],[1,0.7]],[[0,0.25],[1,0.75]],[[0,0.15],[1,0.85]],[[0,0.1],[1,0.9]]]

        self.m_settings.divy = 2


        print("CMskGenerateSkirtDefMesh called")
        CBaseMskGenerateSkirtMesh.execute(self, context)

        return{"FINISHED"}