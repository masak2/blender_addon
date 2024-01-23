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

    imp.reload(obj_generate_ctr_bones_selected)
    imp.reload(obj_generate_shapekey_bones)

    imp.reload(VIEW3D_tools_varioushelper)

else:
    print("import masak general addon")
    from . import obj_generate_ctr_bones_selected
    from . import obj_generate_shapekey_bones

    from . import VIEW3D_tools_varioushelper

import bpy

#def menu_func(self, context):
#    self.layout.operator(io_export_colour_layout_png.CMskExportColorLayoutPng.bl_idname)

# クラスをまとめる
classes = (
    #obj_generate_ctr_bones.MskGenerateCtrBones,
    obj_generate_ctr_bones_selected.MskGenerateCtrBonesSelected,
    #obj_generate_leg_rig.MskGenerateLegRig,
    obj_generate_shapekey_bones.MskGenerateShapeKeyBones,
    #obj_rename_bones_vroid_to_bl.MskRenameBonesVroidToBL,
    #obj_rename_groups_vroid_to_bl.MskRenameGroupsVroidToBL,

)

# まとめたクラスを一度に登録
register, unregister = bpy.utils.register_classes_factory(classes)

#if __name__ == "__main__":
    #register()
