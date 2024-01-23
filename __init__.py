bl_info = {
    "name": "Masak GeneralAddon",
    "author": "Masashi Kamiyama( masak )",
    "version": (1,0),
    "blender": (4, 00, 0),
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


else:
    print("import masak general addon")
    from . import obj_generate_ctr_bones_selected
    from . import obj_generate_shapekey_bones


import bpy

def menu_func(self, context):
    self.layout.operator(obj_generate_ctr_bones_selected.MskGenerateCtrBonesSelected.bl_idname, text="Masak Gen Ctr Bones")
    self.layout.operator(obj_generate_shapekey_bones.MskGenerateShapeKeyBones.bl_idname, text="Masak Gen ShapeKey Bones")

# クラスをまとめる
classes = (
    obj_generate_ctr_bones_selected.MskGenerateCtrBonesSelected,
    obj_generate_shapekey_bones.MskGenerateShapeKeyBones,

)

# まとめたクラスを一度に登録 4.0だとF3 Serachに出ない…
#register, unregister = bpy.utils.register_classes_factory(classes)

def register():
    bpy.utils.register_class(obj_generate_ctr_bones_selected.MskGenerateCtrBonesSelected)
    bpy.utils.register_class(obj_generate_shapekey_bones.MskGenerateShapeKeyBones)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(obj_generate_ctr_bones_selected.MskGenerateCtrBonesSelected)
    bpy.utils.unregister_class(obj_generate_shapekey_bones.MskGenerateShapeKeyBones)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
