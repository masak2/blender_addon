#-------------------------------------------------------------------------------
# Name:        io_export_cutscene
# Purpose:
#
# Author:      masak
#
# Created:     01/01/2016
# Copyright:   (c) masak 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import bpy
import mathutils
from masak.util_various import *
import os

#breakpoint = bpy.types.bp.bp

class CMskExportCutscene(bpy.types.Operator):
##class CMskExportWaypointInfo():
    bl_idname = "masak.msk_io_export_cutscene"
    bl_label = "msk_io_export_cutscene"
    bl_description = "Export cutscene info to [filename].csv"
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
        #fs = open(path, 'w')

        active_scene = context.scene
        scene_fps = active_scene.render.fps

        
        # motion info

        all_arr = []
        # search armature and camera
        for obj in active_scene.objects:
            if obj.type == 'ARMATURE' or obj.type == 'CAMERA':
                print(obj.name)
                ret_arr = self.export_motion(obj, scene_fps)
                for strip_info in ret_arr:
                    all_arr.append(strip_info)

        # camera switch info
        for marker in active_scene.timeline_markers:
            if marker.name.startswith('cam'):
                targetName = marker.camera.name
                startTime = (marker.frame-1) / scene_fps
                elem = [startTime,2,targetName,"", "", 0, 0]
                all_arr.append(elem)

        # play 2DSE
        splitedarr = path.split('\\')
        blend_filename = splitedarr[len(splitedarr) -1]
        blend_filenamewithoutarr = blend_filename.split('.')
        blend_filenamewithout = blend_filenamewithoutarr[0]

        sequence_editor = active_scene.sequence_editor
        if sequence_editor != None:
            sequences = sequence_editor.sequences
            sorted_seqs = sorted(sequences, key=lambda x:x.frame_start)

            for tmp_seq in sorted_seqs:
                if tmp_seq.type == 'SOUND':
                    # print(tmp_seq.filepath)
                    elem = self.export_2dse(tmp_seq, scene_fps, blend_filenamewithout)
                    all_arr.append(elem)

        # play 3dSE
        for obj in active_scene.objects:
            if obj.type == 'SPEAKER' and obj.is_visible(active_scene):
                print(obj.name)
                elem = self.export_3dse(obj, scene_fps, blend_filenamewithout)
                all_arr.append(elem)

        # sort by frame_start
        sorted_allarr = sorted(all_arr, key=lambda x:x[0])

        #path = path.replace('.csv','b.csv')
        fs = open(path,'w')
        fs.write("id,startTime,cmdId,targetName,paramStr0,paramStr1,paramF0,paramF1\n")
        for i,info in enumerate(sorted_allarr):
            fs.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (i,info[0],info[1],info[2],info[3],info[4],info[5],info[6]))



        """
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
        """
        return{'FINISHED'}

    def get_sndid(self, ap_info, snd_name):
        for snd_info in ap_info:
            if snd_info[2] == snd_name:
                return snd_info[0]
        return "0"

    def export_motion(self, char_obj, fps):
        ret_arr = []
        for nlatrack in char_obj.animation_data.nla_tracks:
            print(nlatrack.name)
            for strip in nlatrack.strips:
                if strip.action.name.find("proxyAction") != -1:
                    continue
                frameStart = (strip.frame_start - 1 )/fps
                cmdId = 1
                targetName = char_obj.name
                if char_obj.type == 'ARMATURE':
                    targetName = char_obj["targetName"]
                strip_info= [frameStart,cmdId, targetName, strip.action.name, "", 0, 0]
                ret_arr.append(strip_info)
                #fs.write("%s,%s,%s\n" % (char_id, strip.action.name, strip.frame_start/24))
        return ret_arr
    def export_2dse(self, se_obj, fps, blend_filename):
        startTime = se_obj.frame_start / fps
        cmdID = 5
        start = 2
        filename = se_obj.name
        idx = filename.find('.')
        filepath = "cutscene/" + blend_filename + "/" + filename[0:idx]
        return [startTime, cmdID, "", filepath, "", se_obj.volume, se_obj.pitch]
    def export_3dse(self, se_obj, fps, blend_filename):
        for nlatrack in se_obj.animation_data.nla_tracks:
            for strip in nlatrack.strips:
                startTime = (strip.frame_start -1) / fps
                speaker = se_obj.data
                #print('export_3dse ' + se_obj.name + ' t=' + se_obj.type)
                #print(speaker.attenuation)
                filename = speaker.sound.filepath
                #print('se path=' + filename)

                start = 2
                idx = filename.find('.')
                # qiitaに騙された。嘘書きやがって
                filepath = "cutscene/" + blend_filename + "/" + filename[start:idx]

                constraints = se_obj.constraints
                cmdId = -1

                if len(constraints) == 0:
                    #　単純にワールドＳＥ再生
                    cmdId = 3
                    pos = se_obj.location
                    posStr = str(pos.x) + "/" + str(pos.z) + "/" + str(pos.y)
                    return [startTime, cmdId, "", filepath,posStr,speaker.volume,speaker.pitch]
                else:
                    # 指定キャラからボイス再生
                    if len(constraints) != 1:
                        print('constraint is limited to 1 len=' + str(len(constraints)))

                    c = constraints[0]
                    if c.type != 'COPY_TRANSFORMS':
                        print('only COPY_TRANSFORMS is allowed')

                    
                    targetName = c.target.name
                    cmdId = 4
                    return [startTime, cmdId, targetName, filepath,"",speaker.volume,speaker.pitch] 


                

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
