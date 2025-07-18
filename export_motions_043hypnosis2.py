
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
    export_arp(filepath, rig_name, anim_name_key)


def SafeSelectAndExportAyaka(anim_name_key):
    SafeSelectAndExport("CGIR00100_Kikyo_rig","ArmatureCGIR00100","CGIR00100", anim_name_key)

def SafeSelectAndExportAyakaTitty(anim_name_key):
    SafeSelectAndExport("CGIR00110_Kikyo_rig","ArmatureCGIR00110","CGIR00110", anim_name_key)

def SafeSelectAndExportEri(anim_name_key):
    SafeSelectAndExport("CGIR00200_Eri_rig","ArmatureCGIR00200","CGIR00200", anim_name_key)


def SafeSelectAndExportHero(anim_name_key):
    SafeSelectAndExport("CMAN00100_rig","ArmatureCMAN00100","CMAN00100", anim_name_key)

def SafeSelectAndExportBicycle(anim_name_key):
    SafeSelectAndExport("ArmatureBicycle","ArmatureBicycle","CMAN00300", anim_name_key)

def unselect_all():
    for obj in bpy.data.objects:
        obj.select_set( False)

def select_and(objname):
    obj =     bpy.data.objects[objname]
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def export_arp(file_output, rig_name, anim_name_key):
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
    scn.arp_only_containing = True
    scn.arp_export_name_string = anim_name_key# CGIR00100
    
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
    bpy.ops.id.arp_export_fbx_panel(filepath= file_output)

def GetFilePath(fileName):
    blendpath = bpy.data.filepath
    index = blendpath.rfind("\\")
    dir_name = blendpath[0: index+1]
    filepath = dir_name + fileName + ".fbx"
    return filepath

    