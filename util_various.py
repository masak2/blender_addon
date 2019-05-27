#-------------------------------------------------------------------------------
# Name:        util_various
# Purpose:
#
# Author:      masak
#
# Created:     08/10/2011
# Copyright:   (c) masak 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import bpy

def msk_util_print(message):
    print("//-------------------------------------------")
    print("// " + message)
    print("//-------------------------------------------")
def msk_util_warning(message):
    print("鬯ｮ・ｫ繝ｻ・ｨ驛｢譎｢・ｽ・ｻ郢晢ｽｻ繝ｻ・｣郢晢ｽｻ繝ｻ・ｰWarning")
    print("鬯ｮ・ｫ繝ｻ・ｨ驛｢譎｢・ｽ・ｻ郢晢ｽｻ繝ｻ・｣郢晢ｽｻ繝ｻ・ｰWarning: " + message)
    print("鬯ｮ・ｫ繝ｻ・ｨ驛｢譎｢・ｽ・ｻ郢晢ｽｻ繝ｻ・｣郢晢ｽｻ繝ｻ・ｰWarning")
def msk_util_set_layer(obj, layer_index):
    obj.layers[layer_index] = True
    for i in range(0, len(obj.layers)):
        if i != layer_index:
            obj.layers[i] = False

def msk_util_noselect():
    for obj in bpy.data.objects:
        obj.select = False

def msk_util_select_only(obj_name):
    for obj in bpy.data.objects:
        obj.select = (obj.name == obj_name)

def msk_util_activate(obj, scene):
    scene.objects.active = obj
    pass

def msk_util_newmodifier_if_no_exist( obj, name0, type0 ):
    if obj == None:
        return
    bHasModi = False
    for modifier in obj.modifiers:
        if modifier.type == type0:
            bHasModi = True
            break
    if bHasModi == False:
        obj.modifiers.new(name=name0, type=type0)

def main():
    pass

if __name__ == '__main__':
    main()
