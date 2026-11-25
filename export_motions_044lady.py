
import bpy
from collections import Counter
import os
#rig_object_name:"CGIR00100_Kikyo_rig"
#rig_name:"ArmatureCGIR00100"
#filepath_key:"CGIR00100"
#anim_name_key:"CGIR00100@ESEX51010"
#
def SafeSelectAndExport(rig_object_name, rig_name, filepath_key, anim_name_key):
    unselect_all();
    select_and(rig_object_name)
    filepath = GetFilePath(anim_name_key);
    convert_axis = True
    if filepath_key == "CMAN00400":
        convert_axis = False
    export_arp(filepath, rig_name, anim_name_key, convert_axis)


def SafeSelectAndExportSonia(anim_name_key):
    SafeSelectAndExport("CGIR00100_Sonia_rig","ArmatureCGIR00100","CGIR00100", anim_name_key)

def SafeSelectAndExportSoniaTitty(anim_name_key):
    SafeSelectAndExport("CGIR00110_Sonia_rig","ArmatureCGIR00110","CGIR00110", anim_name_key)



def SafeSelectAndExportSyota(anim_name_key):
    SafeSelectAndExport("CMAN00100_Yuta_rig","ArmatureCMAN00100","CMAN00100", anim_name_key)
def SafeSelectAndExportBadGuy(anim_name_key):
    SafeSelectAndExport("CMAN00200_BadGuy_rig","ArmatureCMAN00200","CMAN00200", anim_name_key)
def SafeSelectAndExportDQN(anim_name_key):
    SafeSelectAndExport("CMAN00300_DQN_rig","ArmatureCMAN00300","CMAN00300", anim_name_key)
def SafeSelectAndExportSlime(anim_name_key):
    SafeSelectAndExport("CMAN00400_Slime_rig","ArmatureCMAN00400","CMAN00400", anim_name_key)

def SafeSelectAndExportSyotaSonia(anim_name_keyHero,anim_name_keyAyaka):
    mute_tracks_without("CMAN00100_Yuta_rig", anim_name_keyHero)
    mute_tracks_without("CGIR00100_Sonia_rig", anim_name_keyAyaka)
    SafeSelectAndExportSyota(anim_name_keyHero)
    SafeSelectAndExportSonia( anim_name_keyAyaka)

def SafeSelectAndExportBadGuySonia(anim_name_keyHero,anim_name_keyAyaka):
    mute_tracks_without("CMAN00200_BadGuy_rig", anim_name_keyHero)
    mute_tracks_without("CGIR00100_Sonia_rig", anim_name_keyAyaka)
    SafeSelectAndExportBadGuy(anim_name_keyHero)
    SafeSelectAndExportSonia( anim_name_keyAyaka)

def SafeSelectAndExportDQNSonia(anim_name_keyHero,anim_name_keyAyaka):
    mute_tracks_without("CMAN00300_DQN_rig", anim_name_keyHero)
    mute_tracks_without("CGIR00100_Sonia_rig", anim_name_keyAyaka)
    SafeSelectAndExportDQN(anim_name_keyHero)
    SafeSelectAndExportSonia( anim_name_keyAyaka)

def SafeSelectAndExportSlimeSonia(anim_name_keyHero,anim_name_keyAyaka):
    mute_tracks_without("CMAN00400_Slime_rig", anim_name_keyHero)
    mute_tracks_without("CGIR00100_Sonia_rig", anim_name_keyAyaka)
    SafeSelectAndExportSlime(anim_name_keyHero)
    SafeSelectAndExportSonia( anim_name_keyAyaka)

def mute_tracks_without(rig_name, track_name):
    obj = bpy.data.objects.get(rig_name)

    if not obj or obj.type != 'ARMATURE':
        raise Exception("指定したArmatureが見つかりません")

    if not obj.animation_data or not obj.animation_data.nla_tracks:
        raise Exception("NLAトラックが存在しません")

    for track in obj.animation_data.nla_tracks:
        track.mute = (track.name != track_name)

    print(f"NLA Track '{track_name}' のみ有効化しました")

def unselect_all():
    for obj in bpy.data.objects:
        obj.select_set( False)

def select_and(objname):
    obj =     bpy.data.objects[objname]
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def export_arp(file_output, rig_name, anim_name_key, convert_axis):
    # set the file path output here
    # set some settings...
    scn = bpy.context.scene
    scn.arp_export_rig_type = 'HUMANOID'
    scn.arp_ge_sel_only = True
    # types: 'humanoid', 'mped'
    scn.arp_engine_type = 'UNITY'
    scn.arp_bake_anim = True
    scn.arp_bake_type = "ACTIONS"
    scn.arp_bake_only_active = False
    scn.arp_export_rig_name = rig_name#"ArmatureCPLA00100" 
    scn.arp_export_separate_fbx = True
    scn.arp_export_file_separator = "NONE"
    #scn.arp_only_containing = True
    scn.arp_export_name_string = anim_name_key# CGIR00100
    scn.arp_init_fbx_rot = convert_axis
    
    # bpy.context.scene.arp_keep_bend_bones = True
# bpy.context.scene.arp_units_x100 = True
# bpy.context.scene.arp_bake_actions = True
# bpy.context.scene.arp_export_name_actions = True
# bpy.context.scene.arp_export_name_string = "ArmatureCPLA00100"
# bpy.context.scene.arp_mesh_smooth_type = 'EDGE'
# bpy.context.scene.arp_ue_root_motion = True
# bpy.context.scene.arp_export_noparent = True
# bpy.context.scene.arp_export_twist = True
    # export it
    bpy.ops.arp.arp_export_fbx_panel(filepath= file_output)

def GetFilePath(fileName):
    blendpath = bpy.data.filepath
    index = blendpath.rfind("\\")
    dir_name = blendpath[0: index+1]
    filepath = dir_name + fileName + ".fbx"
    return filepath

    