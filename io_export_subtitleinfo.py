#-------------------------------------------------------------------------------
# Name:        io_export_subtitleinfo
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

class CMskExportSubtitleInfo(bpy.types.Operator):
##class CMskExportWaypointInfo():
    bl_idname = "masak.msk_io_export_subtitleinfo"
    bl_label = "msk_io_export_subtitleinfo"
    bl_description = "Export subtitle info to [filename].csv"
    bl_context = "objectmode"


    def execute(self, context):
        msk_util_print(self.bl_idname)

#
        # export format
        # int vertexindex, int[] connected_vertex_indices
        #
        path = bpy.data.filepath
        if path != '':
            path = path.replace('.blend','.csv')

        print(path)
        fs = open(path, 'w')

        active_scene = context.scene
        sequence_editor = active_scene.sequence_editor
        sequences = sequence_editor.sequences
        sorted_seqs = sorted(sequences, key=lambda x:x.frame_start)

        for tmp_seq in sorted_seqs:
            if tmp_seq.type == 'SOUND' and tmp_seq.sound.name.startswith("ev"):
                # print(tmp_seq.filepath)
                fs.write("%s,%s,%s\n" % (tmp_seq.sound.name, tmp_seq.frame_start/24, tmp_seq.volume))

        # motion info

        all_arr = []
        # search armature
        if "cp03" in bpy.data.objects:
            eila = bpy.data.objects["cp03"]
            ret_arr = self.export_motion(fs,eila,2)
            for strip_info in ret_arr:
                all_arr.append(strip_info)

        if "cp01" in bpy.data.objects:
            sanya = bpy.data.objects["cp01"]
            ret_arr = self.export_motion(fs,sanya,1)
            for strip_info in ret_arr:
                all_arr.append(strip_info)

        if "ce01" in bpy.data.objects:
            warlock = bpy.data.objects["ce01"]
            ret_arr = self.export_motion(fs, warlock,3)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        if "ce02_neuroi_girl" in bpy.data.objects:
            neuroigirl = bpy.data.objects["ce02_neuroi_girl"]
            ret_arr = self.export_motion(fs,neuroigirl,4)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        if "ce03" in bpy.data.objects:
            neuroi10 = bpy.data.objects["ce03"]
            ret_arr = self.export_motion(fs,neuroi10,5)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        if "ce04" in bpy.data.objects:
            neuroixx = bpy.data.objects["ce04"]
            ret_arr = self.export_motion(fs,neuroixx,9)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        # special
        if "m10_Armature_floor" in bpy.data.objects:
            wall0 = bpy.data.objects["m10_Armature_floor"]
            ret_arr = self.export_motion(fs, wall0, 13)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        if "m10_lounge_inside_brokenwall_0" in bpy.data.objects:
            wall1 = bpy.data.objects["m10_lounge_inside_brokenwall_0"]
            ret_arr = self.export_motion(fs, wall1, 14)
            for strip_info in ret_arr:
                all_arr.append(strip_info)
        # sort by frame_start
        sorted_allarr = sorted(all_arr, key=lambda x:x[2])

        path = path.replace('.csv','b.csv')
        fs = open(path,'w')
        fs.write("ID,CharcterID,AnimName,FrameStart,\n")
        for i,frame_info in enumerate(sorted_allarr):
            fs.write("%s,%s,%s,%s\n" % (i,frame_info[0],frame_info[1],frame_info[2]))

        #  se info & camera switch info

        # get sound info from Sound.csv
        path_sndcsv = "C:/Users/masak/Dropbox/002_SW/Planner/Parameter/Sound.csv"
        fs = open(path_sndcsv,'r')
        aszLines = fs.readlines()
        fs.close()
        ap_info = []
        for line in aszLines:
            snd_info = line.split(',')
            ap_info.append(snd_info)


        path = path.replace('b.csv', 'c.csv')
        fs = open(path,'w')
        fs.write("ID,CommandID,Param,SoundID,SoundName,FrameStart,Volume\n")
        all_arr = []
        index = 0
        for tmp_seq in sorted_seqs:
            if tmp_seq.type == 'SOUND' and tmp_seq.sound.name.startswith("ev") == False:
                print(tmp_seq.filepath)
                sndfilename = tmp_seq.sound.name.replace(".wav","")
                sndfilename = sndfilename.replace(".ogg","")
                sndfilename = sndfilename.replace(".mp3", "")
                sndid = self.get_sndid(ap_info, sndfilename)
                elem = [index,250,"",sndid, sndfilename, tmp_seq.frame_start/24, tmp_seq.volume]
                all_arr.append(elem)
                #fs.write("%s,%s,%s,%s,%s,%s,%s\n" % ())
                index = index + 1

        # camera switch
        for marker in active_scene.timeline_markers:
            cameraname = marker.camera.name
            elem = [index,226,cameraname,0, "", marker.frame/24, 0]
            all_arr.append(elem)
            #fs.write("%s,%s,%s,%s,%s,%s,%s\n" % ())
            index = index + 1
        # effect emit
        effobj_arr = []
        for objTmp in bpy.data.objects:
            if objTmp.name.startswith("effect"):
                effobj_arr.append(objTmp)
        for effobj in effobj_arr:
            ret_emit_arr = self.export_effect(fs, effobj)
            for emit_info in ret_emit_arr:
                param = "["
                for i in range(2,8):
                    if i == 7:
                        param += str(emit_info[i])
                    else:
                        param += str(emit_info[i]) + "/"
                param += "]"

                elem = [index,337,param, emit_info[1], "", emit_info[0]/24, 0]
                all_arr.append(elem)
                index = index + 1

        sorted_allarr = sorted(all_arr, key=lambda x:x[5])

        for elem in sorted_allarr:
            sz_line = ""
            for i, sz in enumerate(elem):
                sz_line = sz_line + "%s" % (sz)
                if i != len(elem)-1:
                    sz_line = sz_line + ","
                else:
                    sz_line = sz_line + "\n"
            fs.write(sz_line)
        return{'FINISHED'}

    def get_sndid(self, ap_info, snd_name):
        for snd_info in ap_info:
            if snd_info[2] == snd_name:
                return snd_info[0]
        return "0"

    def export_motion(self, fs, char_obj, char_id):
        ret_arr = []
        for nlatrack in char_obj.animation_data.nla_tracks:
            print(nlatrack.name)
            for strip in nlatrack.strips:
                if strip.action.name.find("proxyAction") != -1:
                    continue
                strip_info= [char_id, strip.action.name, strip.frame_start/24]
                ret_arr.append(strip_info)
                #fs.write("%s,%s,%s\n" % (char_id, strip.action.name, strip.frame_start/24))
        return ret_arr
    def export_effect(self,fs,eff_obj):
        ret_emit_arr = []
        for nlatrack in eff_obj.animation_data.nla_tracks:
            print(nlatrack.name)
            for strip in nlatrack.strips:
                start_frame = strip.frame_start
                action = strip.action
                emit_arr = []
                for fcurve in action.fcurves:
                    if fcurve.data_path == '["emit"]':
                        for keyframe in fcurve.keyframe_points:
                            #emit_frame = start_frame + keyframe.co[0] wrong
                            emit_frame = keyframe.co[0]
                            #print("startframe="+str(start_frame) + " keyframe="+str(keyframe.co[0]))
                            effectid = keyframe.co[1]
                            if effectid >= 1:
                                # frame, id, x, y, z,  rx, ry, rz
                                elem = [emit_frame, effectid, 0, 0, 0, 0, 0, 0]
                                emit_arr.append(elem)
                        break
                for emit_elem in emit_arr:
                    tmp_start_frame = emit_elem[0] - start_frame
                    for fcurve in action.fcurves:
                        if fcurve.data_path == '["emit"]':
                            continue
                        index = 0
                        if fcurve.data_path == "location":
                            index = 2 + fcurve.array_index
                        elif fcurve.data_path == "rotation_euler":
                            index = 5 + fcurve.array_index
                        if index > 0:
                            emit_elem[index] = fcurve.evaluate(tmp_start_frame)
                        else:
                            print("invalid index! nlaname=" + strip.name + " fcurve_datapath=" + fcurve.data_path)
            ret_emit_arr += emit_arr
        return ret_emit_arr

def main():
    instance = CMskExportSubtitleInfo()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()
