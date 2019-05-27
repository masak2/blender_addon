#-------------------------------------------------------------------------------
# Name:        io_export_waypoint_info
# Purpose:
#
# Author:      masak
#
# Created:     05/06/2012
# Copyright:   (c) masak 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import bpy
import mathutils
from masak.util_various import *
import os

breakpoint = bpy.types.bp.bp

class CMskExportWaypointInfo(bpy.types.Operator):
##class CMskExportWaypointInfo():
    bl_idname = "masak.msk_io_export_waypoint_info"
    bl_label = "msk_io_export_waypoint_info"
    bl_description = "Export waypoint info to [object_name].txt, plz select mesh objects"
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

        src_objs = context.selected_objects
        for obj in src_objs:
            if obj.type != 'MESH':
                continue

            mesh = obj.data

            #
            # export format
            # int vertexindex, int[] connected_vertex_indices
            #
            path = bpy.data.filepath
            if path != '':
                path = os.path.dirname(path)
                path ="%s/%s.txt" % (path,obj.name)
            else:
                # blender.app 驍ｵ・ｺ繝ｻ・ｮ髯懶ｽ｣繝ｻ・ｴ髫ｰ繝ｻﾂ驍ｵ・ｺ繝ｻ・ｫ
                path = "%s.txt" % obj.name

            print(path)
            fs = open(path, 'w')
            fs.write("{")

            # vertex
            fs.write("\"total\":%d," % len(mesh.vertices))
            iEnd = len(mesh.vertices)
            iIndex = 0
            for meshvertex in mesh.vertices:
                fs.write("\"%s\":{" % meshvertex.index)

                fs.write("\t\"vidx\":%d," % meshvertex.index)
                # unity editor 髣包ｽｳ驗呻ｽｫ邵ｲ蟶晢ｽｫ・ｫ闕ｳ・ｻ繝ｻ・ｱ繝ｻ・､髯具ｽｹ隰費ｽｶ隨倥・・ｹ・ｧ闕ｵ譏ｴ繝ｻ驍ｵ・ｺ繝ｻ・ｧ驍ｵ・ｺ髦ｮ蜻ｻ・ｼ繝ｻ・ｸ・ｺ繝ｻ・ｮworld coordination 驍ｵ・ｺ繝ｻ・ｯ髴取ｻゑｽｽ・｡鬯ｯ・ｧ郢晢ｽｻ遶企豪・ｸ・ｺ繝ｻ・ｪ驛｢・ｧ郢晢ｽｻ
                #wco = obj.matrix_world * meshvertex.co
                #fs.write("\t\"pos\":[%f,%f,%f]," % (wco[0], wco[1], wco[2]))
                fs.write("\t\"pos\":[%f,%f,%f]," % (meshvertex.co[0],meshvertex.co[1],meshvertex.co[2]))
                bLerpNormal = self.IsLerpNormal(obj, meshvertex.index)
                szTmp = ""
                if bLerpNormal:
                    szTmp = "true"
                else:
                    szTmp = "false"

                fs.write("\t\"lerp_normal\":" + szTmp + ",")

                fs.write("\t\"connected_vidx\":[")

                tmp_arr = []
                for meshedge in mesh.edges:

                    if meshvertex.index in meshedge.vertices:
                        for vidx in meshedge.vertices:
                            if vidx != meshvertex.index:
                                tmp_arr.append(vidx)

                iTotal = len(tmp_arr)
                for i in range(iTotal):
                    vidx = tmp_arr[i]
                    if i != iTotal-1:
                        fs.write("%d," % vidx)
                    else:
                        fs.write("%d" % vidx)
                #if iIndex == iEnd - 1:
                #    fs.write("]}")
                #else:
                #    fs.write("]},")
                fs.write("]},")
                iIndex += 1

            # edge
            fs.write("\"edge_total\":%d," % len(mesh.edges))
            iEnd = len(mesh.edges)
            iIndex = 0
            for meshedge in mesh.edges:
                fs.write("\"e%s\":{" % meshedge.index)

                fs.write("\t\"eidx\":%d," % meshedge.index)
                local_normal = self.get_localnormal(obj, meshedge.index)
                fs.write("\t\"local_normal\":[%f,%f,%f]," % local_normal)
                fs.write("\t\"vidxs\":[%d,%d]" % (meshedge.vertices[0],meshedge.vertices[1]))
                if iIndex == iEnd - 1:
                    fs.write("}")
                else:
                    fs.write("},")
                iIndex += 1
            fs.write("}")


        return{'FINISHED'}

    #   邵ｺ阮吶・鬯・ｉ縺帷ｸｺ・ｯ lerp normal 騾包ｽｨ邵ｺ繝ｻ
    #   idx : 鬯・ｉ縺帷ｸｺ・ｮ郢ｧ・､郢晢ｽｳ郢昴・縺醍ｹｧ・ｹ
    #   隰鯉ｽｻ郢ｧ髮・・､ : true lerp normal 騾包ｽｨ
    def IsLerpNormal(self, obj, idx):
        # 邵ｺ・ｾ邵ｺ螢ｹ繝ｻ lerp_normal 邵ｺ・ｮ group index 郢ｧ螳夲ｽｪ・ｿ邵ｺ・ｹ郢ｧ繝ｻ
        group_normal_idx = -1
        for vgroup in  obj.vertex_groups:
            if vgroup.name == "lerp_normal":
                group_normal_idx = vgroup.index
                break
        mesh = obj.data
        bRet = False
        for mesh_vertex in mesh.vertices:
            if mesh_vertex.index == idx:
                for vge in mesh_vertex.groups:
                    if vge.group == group_normal_idx:
                        bRet = True
                        break
        return bRet

    #
    #   隰悶・・ｮ蝟ｨndex 邵ｺ・ｮ edge 邵ｺ・ｮ normal 郢ｧ螳夲ｽｿ譁絶・
    def get_localnormal(self, obj, idx):
        mesh = obj.data
        vidxs = []
        for meshedge in mesh.edges:
            if meshedge.index == idx:
                vidxs = meshedge.vertices
                break

        #  陷茨ｽｱ鬨ｾ螢ｹ繝ｻ vertex group index 郢ｧ蜻茨ｽｱ繧・ｽ∫ｹｧ荵敖ﾂ邵ｺ・ｾ邵ｺ窶賄ge 邵ｺ・ｫ隲繝ｻ・ｰ・ｱ隰問・笳・ｸｺ蟶呻ｽ臥ｹｧ蠕鯉ｽ檎ｸｺ・ｰ隶鯉ｽｽ邵ｺ・ｪ郢ｧ阮吮味邵ｺ繝ｻ
        idx = vidxs[0]
        vgi_arr0 = []
        for vge in mesh.vertices[idx].groups:
            vgi_arr0.append(vge.group)
        #print("vgi_arr0 %d\n" % (vidxs[0]))
        #print(vgi_arr0)
        vgi_set0 = set(vgi_arr0)

        idx = vidxs[1]
        vgi_arr1 = []
        for vge in mesh.vertices[idx].groups:
            vgi_arr1.append(vge.group)
        #print("vgi_arr1 %d\n" % (vidxs[1]))
        #print(vgi_arr1)
        vgi_set1 = set(vgi_arr1)

        # 郢昴・繝ｻ郢ｧ・ｿ邵ｺ譴ｧ・ｭ・｣邵ｺ蜉ｱ・樒ｸｺ・ｪ郢ｧ迚吶・鬨ｾ螟奇ｽｦ竏ｫ・ｴ・ｰ邵ｺ・ｯ1陋滉ｹ昶味邵ｺ繝ｻ
        com_set = vgi_set0 & vgi_set1
        print("**common_element** is %d" % (len(com_set)))
        com_arr = list(com_set)
        com_vgidx = com_arr[0]

        vertex_group = obj.vertex_groups[com_vgidx]

        aszTmp = vertex_group.name.split('_')
        x = float(aszTmp[0])
        y = float(aszTmp[1])
        z = float(aszTmp[2])
        # blender 縺ｯ蜿ｳ謇狗ｳｻ縲「nity 縺ｯ蟾ｦ謇狗ｳｻ縲・ 繧貞渚霆｢縺輔○縺ｪ縺・→縺翫°縺励￥縺ｪ繧・
        #z = -z
        #mtx4_z90 = Matrix.Rotation(math.pi / 2.0, 4, 'Z')
        # 魔法のマトリクスをかける
        mat = mathutils.Matrix()
        mat[0][0:3] = -1.0, 0.0, 0.0
        mat[1][0:3] = 0.0, 0.0, 1.0
        mat[2][0:3] = 0.0, -1.0, 0.0
        #print(mat)

        vec = mathutils.Vector((x,y,z))
        vec.normalize()
        #vec = mtx4_z90 * vec
        vec = mat * vec
        vec.normalize()
        print("local_normal %f %f %f **** %f %f %f" % (x,y,z, vec.x, vec.y, vec.z))
        x = vec.x
        y = vec.y
        z = vec.z
        return (x,y,z)


def main():
    instance = CMskExportWaypointInfo()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
