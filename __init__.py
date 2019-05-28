bl_info = {
    "name": "Masak GeneralAddon",
    "author": "Masashi Kamiyama( masak )",
    "version": (1,0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Masak VariousHelper",
    "description": "various helper class and method for various projects",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Object/Cloud_Gen",
    "tracker_url": "https://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=22015",
    "category": "Object"}


print("/**********************************************************")
print("Masak GeneralAddon")
print("/**********************************************************")
if "bpy" in locals():
    import imp
    import sys
    print("reload masak general addon")
##    for fqname in sys.modules.keys():
##        print(fqname)

    #imp.reload(anim_plot_action)
    imp.reload(arm_add_stretch2constraint)
    imp.reload(arm_switch_usedeform)
    imp.reload(cur_generate_hair)
    #imp.reload(io_export_colour_layout_png)
    #imp.reload(io_export_fbx)
    #imp.reload(io_export_bonelength)
    imp.reload(io_export_curve)
    #imp.reload(io_export_diffmap)
    imp.reload(io_export_cutscene)
    #imp.reload(io_export_subtitleinfo)
    #imp.reload(io_export_waypoint_info)
    #imp.reload(io_pre_export_fbx)
    #imp.reload(io_pre_remove_image)
    imp.reload(msh_add_vertexgroup_inmesh)
    imp.reload(msh_mirror_vertex_group)
    imp.reload(msh_remove_all_r_vertexgroup)
    imp.reload(obj_generate_ctr_bones)
    imp.reload(obj_generate_leg_rig)
    imp.reload(obj_generate_skirt_bone)
    imp.reload(obj_generate_skirt_mesh)
    imp.reload(obj_remove_ignoreautoweight_vg)
    imp.reload(util_count_bone)
    imp.reload(util_export_project_fbx)
    imp.reload(util_various)
    #imp.reload(vertex_color_vgroup_autoset)

    imp.reload(VIEW3D_tools_varioushelper)

else:
    print("import masak general addon")
    #from . import anim_plot_action
    from . import arm_add_stretch2constraint
    from . import arm_switch_usedeform
    from . import cur_generate_hair
    #from . import io_export_colour_layout_png
    #from . import io_export_fbx
    #from . import io_export_bonelength
    from . import io_export_curve
    #from . import io_export_diffmap
    from . import io_export_cutscene
    #from . import io_export_subtitleinfo
    #from . import io_export_waypoint_info
    #from . import io_pre_export_fbx
    #from . import io_pre_remove_image
    from . import msh_add_vertexgroup_inmesh
    from . import msh_mirror_vertex_group
    from . import msh_remove_all_r_vertexgroup
    from . import obj_generate_ctr_bones
    from . import obj_generate_leg_rig
    from . import obj_generate_skirt_bone
    from . import obj_generate_skirt_mesh
    from . import obj_remove_ignoreautoweight_vg
    from . import util_count_bone
    from . import util_export_project_fbx
    from . import util_various
    #from . import vertex_color_vgroup_autoset

    from . import VIEW3D_tools_varioushelper

import bpy

#def menu_func(self, context):
#    self.layout.operator(io_export_colour_layout_png.CMskExportColorLayoutPng.bl_idname)

# クラスをまとめる
classes = (
    obj_generate_ctr_bones.MskGenerateCtrBones,
    obj_generate_leg_rig.MskGenerateLegRig,
)

# まとめたクラスを一度に登録
register, unregister = bpy.utils.register_classes_factory(classes)

#if __name__ == "__main__":
    #register()
