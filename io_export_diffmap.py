#-------------------------------------------------------------------------------
# Name:        io_export_diffmap
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

from mathutils import Vector, Color
import time
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper
import os
import os.path

__version__ = '1.1.2'
class CMskExportDiffmap(bpy.types.Operator):
##class CMskExportWaypointInfo():
    bl_idname = "masak.msk_io_export_diffmap"
    bl_label = "msk_io_export_diffmap"
    bl_description = "Export morph info to [filename].csv and *.tga and more"
    bl_context = "objectmode"

    original_materials = []
    mat = None
    original_face_mat_indices = []
    ShapeKeyName = []
    MaxDiffStore = []

    #---------------------------------------------------------------------------
    # 実行部
    #---------------------------------------------------------------------------
    def execute(self, context):
        msk_util_print(self.bl_idname)

        ob = context.active_object
        scene = context.scene

        print("-----------------------------------------------------")
        print("Starting Diff-Map export for object %s ..." % ob.name )

        absfilepath = bpy.data.filepath
        dirpath = ''
        if absfilepath != '':
            dirpath = os.path.dirname(absfilepath)
        # Error checking
        if self.found_error( context, dirpath):
            print(self.found_error( context, dirpath))
            # todo return {'ERROR' } が理想
            return{'FINISHED'}

        self.pre(ob)

        dirpath = dirpath + "/shapekey"
        print("dirpath=" + dirpath + "\n")
        shape = ob.active_shape_key
        name = ob.name
        width = 128
        height = 128
        margin = 10
        animationson = False
        shapeson = True
        #filepath = self.filepath
        #name = self.name
        #width = self.width
        #height = self.height
        #margin = self.margin
        #animationson = self.animationson
        #shapeson = self.shapeson

        self.ShapeKeyName = []
        self.MaxDiffStore = []

        for n in ob.data.shape_keys.key_blocks:
            if n.name != 'Basis': # Skip the 'Basis' shape
                self.generate_diffmap_from_shape(ob, dirpath, name, n, shapeson, width, height, margin )

        self.post(ob)

        self.Write_ShapekeyInfo(dirpath)
        self.Write_ShapekeyAction(dirpath)
        if animationson == True:
            self.Write_Animation(dirpath, name)

        print(" Finished.")
        print("-----------------------------------------------------")
        return{'FINISHED'}

    # ------------------------------------ core functions ------------------------------------

    # Find faces that use the given vertex
    # Returns: tuple with face_index and vertex_index
    def vertex_find_connections(self, mesh, vert_index):

        list = []

        for n in mesh.polygons:
            for i in range( len(n.vertices) ):
                if n.vertices[i] == vert_index:
                    list.append( (n.index, i ) )
        return list


    # Remember and set up things
    #   Deselect all verts
    #   Remember materials
    #   Create temp vertex color layer
    def pre(self, ob):
        print("Prep work started...")

        mesh = ob.data
        uvtex = mesh.uv_textures.active
        vcol = mesh.vertex_colors.active

        global original_materials, mat
        global original_face_mat_indices

        # Deselect all vertices (to avoid odd artefacts, some bug?)
        for n in mesh.vertices:
            n.select = False

        # Store face material indices
        original_face_mat_indices = []
        for n in mesh.polygons:
            original_face_mat_indices.append( n.material_index )
            n.material_index = 0

        # Remember and remove materials
        original_materials = []
        for n in mesh.materials:
            print("Saving Material: " + n.name)
            original_materials.append(n)

        for n in mesh.materials:
            mesh.materials.pop(index=0)

        # Create new temp material for baking
        mat = bpy.data.materials.new(name="DiffMap_Bake")
        mat.use_vertex_color_paint = True
        mat.diffuse_color = Color([1,1,1])
        mat.diffuse_intensity = 1.0
        mat.use_shadeless = True
        mesh.materials.append(mat)


        # Add new vertex color layer for baking
        if len(mesh.vertex_colors) < 8-1:

            vcol = mesh.vertex_colors.new(name="DiffMap_Bake")
            mesh.vertex_colors.active = vcol
            vcol.active_render = True
        else:
            print("Amount limit of vertex color layers exceeded")

        absfilepath = bpy.data.filepath
        shapekeydirpath = os.path.dirname(absfilepath) + "/shapekey"
        if os.path.exists(shapekeydirpath) == False:
            os.mkdir(shapekeydirpath)



    # Restore things
    #   Remove temp materials and restore originals
    #   Remove temp vertex color layer
    def post(self, ob):
        print("Post work started...")

        #global original_materials, mat
        #global original_face_mat_indices

        mesh = ob.data
        uvtex = mesh.uv_textures.active
        vcol = mesh.vertex_colors.active
        original_face_images = []

        # Remove temp material
        mesh.materials.pop(index=0)
        if self.mat != None:
            self.mat.user_clear()
            bpy.data.materials.remove( self.mat )

        # Restore original materials
        for n in self.original_materials:
            mesh.materials.append(n)

        # Restore face material indices
        for n in range(len(self.original_face_mat_indices)-1):
            mesh.polygons[n].material_index = self.original_face_mat_indices[n]

        # Remove temp vertex color layer
        bpy.ops.mesh.vertex_color_remove()


        # Refresh UI
        bpy.context.scene.frame_current = bpy.context.scene.frame_current

        # Free some memory
        self.original_materials = []
        self.original_face_mat_indices = []



    def generate_diffmap_from_shape(self, ob, filepath, name, shape, shapeson, width=128, height=128, margin=10 ):

        #global ShapeKeyName
        #global MaxDiffStore

        mesh = ob.data
        uvtex = mesh.uv_textures.active
        vcol = mesh.vertex_colors.active


        # Find biggest distance offset in shape
        maxdiff = 0.0

        for n in mesh.vertices:

            diff = n.co.copy() - shape.data[n.index].co.copy()
            for i in diff:
                if abs(i) > maxdiff:
                    maxdiff = abs(i)

        if maxdiff > 0:
            self.ShapeKeyName = self.ShapeKeyName + [shape.name]
            self.MaxDiffStore = self.MaxDiffStore + [maxdiff]

        if shapeson == True:
            # Generate vertex color from shape key offset
            for n in mesh.vertices:

                faces = self.vertex_find_connections( mesh, n.index)

                color = Color( [0,0,0] )

                diff = n.co.copy() - shape.data[n.index].co.copy()

                if maxdiff > 0:
                    color[0] = 1.0 - (((diff[0] / maxdiff) + 1.0) *0.5)
                    color[1] = 1.0 - (((diff[1] / maxdiff) + 1.0) *0.5)
                    color[2] = 1.0 - (((diff[2] / maxdiff) + 1.0) *0.5)

                # Apply vertex color to all connected face corners (vertcolors have same structure as uvs)
                for i in faces:
                    vcol.data[n.index].color = color
                '''
                    if i[1] == 0:
                        vcol.data[i[0]].color1 = color
                    if i[1] == 1:
                        vcol.data[i[0]].color2 = color
                    if i[1] == 2:
                        vcol.data[i[0]].color3 = color
                    if i[1] == 3:
                        vcol.data[i[0]].color4 = color
                 '''


            # Create new image to bake to
            image = bpy.data.images.new(name="DiffMap_Bake", width=width, height=height)
            image.generated_width = width
            image.generated_height = height


            # Construct complete filepath

            if str(bpy.app.build_platform).find("Windows") != -1:
                path = filepath + '\\' + name + '-' + shape.name + '.tga'

            elif str(bpy.app.build_platform).find("Linux") != -1:
                path = filepath + '/' + name + '-' + shape.name + '.tga'

            else:
                path = filepath + '/' + name + '-' + shape.name + '.tga'

            image.filepath = path


            # assign image to mesh (all uv faces)
            original_image = uvtex.data[0].image # Simply taking the image from the first face
            original_face_images = []

            for n in uvtex.data:
                if n.image == None:
                    original_face_images.append( None )
                else:
                    original_face_images.append( n.image.name )

                n.image = image


            # Bake
            render = bpy.context.scene.render

            tempcmv = bpy.context.scene.display_settings.display_device

            render.bake_type = 'TEXTURE'
            render.bake_margin = margin
            render.use_bake_clear = True
            render.use_bake_selected_to_active = False
            render.bake_quad_split = 'AUTO'
            bpy.context.scene.display_settings.display_device = 'None'

            bpy.ops.object.bake_image()



            image.save()

            # re-assign images to mesh faces
            for n in range( len(original_face_images) ):

                tmp = original_face_images[n]
                if original_face_images[n] != None:
                    tmp = bpy.data.images[ original_face_images[n] ]
                else:
                    tmp = None

                uvtex.data[n].image = tmp


            # Remove image from memory
            image.user_clear()
            bpy.data.images.remove(image)

            bpy.context.scene.display_settings.display_device = tempcmv

            # Tell user what was exported
            print( " exported %s" % path )


    # General error checking
    def found_error(self, context, dirpath):

        ob = context.active_object
        scene = context.scene
        filepath = dirpath

        if ob.type != 'MESH':
            self.report({'ERROR'}, "Object is not a mesh")
            print("Object is not a mesh")
            return True
        if ob.data.shape_keys == None:
            self.report({'ERROR'}, "Mesh has no shape keys")
            print("Mesh has no shape keys")
            return True
        if len(ob.data.uv_textures) <= 0:
            self.report({'ERROR'}, "Mesh has no UVs")
            print("Mesh has no UVs")
            return True
        if not os.path.exists( filepath ):
            self.report({'ERROR'}, "Invalid filepath: %s" % filepath)
            print("Invalid filepath: %s" % filepath)
            return True
        if len( ob.data.polygons ) <= 0:
            self.report({'ERROR'}, "Mesh contains no faces")
            print("Mesh contains no faces")
            return True

        return False

    def Write_ShapekeyInfo(self, filepath):
        print("-------------------------------")
        print("Starting writing All ShapekeyInfo")

        dstpath = filepath + '/shapekeyinfo.csv'
        fs = open(dstpath,"w")
        fs.write("ID,Name,Multiplier\n")
        for i in range(0,len(self.ShapeKeyName)):
            idtmp = i
            name = self.ShapeKeyName[i]
            multiplier = self.MaxDiffStore[i]
            line = "%i,%s,%f\n" % (idtmp, name, multiplier)
            fs.write(line)

        fs.close
        print("-------------------------------")
        print("End writing All ShapekeyInfo")

    #
    #   shapekey editor にセットされている action を出力
    #
    def Write_ShapekeyAction(self, dirpath):
        print("-------------------------------")
        print("Starting writing All Write_ShapekeyActionAll")

        MyObject = bpy.context.active_object
        activeAction = MyObject.data.shape_keys.animation_data.action
        if activeAction == None:
            print("plz select shapekeyaction in shapekeyEditor")
            return


        dstpath = dirpath + '/' + MyObject.name + "_" + activeAction.name + ".csv"
        fs = open(dstpath, "w")
        fs.write("ID,ShapeKeyID,ShapeKeyName,StartFrame,Length,CurveInfoArr\n")
        AnimationStart = bpy.context.scene.frame_start
        AnimationEnd = bpy.context.scene.frame_end

        start_frame = int(activeAction.frame_range[0])
        end_frame = int(activeAction.frame_range[1])
        n = end_frame - start_frame + 1
        for i,fcurve in enumerate(activeAction.fcurves):
            shapekeyName = fcurve.data_path
            shapekeyName = shapekeyName.replace('key_blocks["', "")
            shapekeyName = shapekeyName.replace('"].value',"")
            shapekeyid = self.ShapeKeyName.index(shapekeyName)
            line = "%i,%i,%s,%i,%i,[" % (i,shapekeyid,shapekeyName,start_frame,n)

            for frame in range(start_frame,n+1):
                tmpvalue =fcurve.evaluate(frame)
                if frame != end_frame:
                    line += "%f/" % (tmpvalue)
                else:
                    line += str(tmpvalue)
            line += "]\n"
            fs.write(line)

        print("-------------------------------")
        print("End writing All Write_ShapekeyActionAll")



    def Write_Animation(self, Afilepath, Afilename):
        ShapeKeyName2 = []
        ShapeKeyName3 = []
        MaxDiffStore2 = []

        print("-------------------------------")
        print("Starting writing Animation List")
        #print("-------------------------------")

        Afileset = Afilepath + '/' + Afilename + '-DiffMapAnimation.TXT'

        # Okay, let's get the base data.
        MyObject = bpy.context.active_object
        MyShapekeys = MyObject.data.shape_keys.key_blocks
        AnimationStart = bpy.context.scene.frame_start
        AnimationEnd = bpy.context.scene.frame_end

        name = self.name

        framestring = str(AnimationStart) + 'to' + str(AnimationEnd)
        Afileset = Afilepath + '/' + Afilename + '-' + framestring + '-DiffMapAnimation.TXT'
        # open the file...
        Animation_Output = open(Afileset,"w")

        for AnimationShapes in range(0, len(self.ShapeKeyName)):
            hasvalue = False
            for AnimationFrame in range(AnimationStart, AnimationEnd + 1):
                bpy.context.scene.frame_set(AnimationFrame)
                if MyShapekeys[self.ShapeKeyName[AnimationShapes]].value > 0.0005:
                    hasvalue = True
            if hasvalue == True:
                ShapeKeyName2 = ShapeKeyName2 + [self.hapeKeyName[AnimationShapes]]
                ShapeKeyName3 = ShapeKeyName3 + [name+"-"+self.ShapeKeyName[AnimationShapes]]
                MaxDiffStore2 = MaxDiffStore2 + [self.MaxDiffStore[AnimationShapes]]

        Animation_Output.write(str(list(ShapeKeyName3)) + "\n")
        Animation_Output.write(str(list(MaxDiffStore2)) + "\n")

        # And loop for every frame of the animation!
        for AnimationFrame in range(AnimationStart, AnimationEnd + 1):
            # Set the current animation frame
            bpy.context.scene.frame_set(AnimationFrame)

            #print("Now working with animation frame: " + str(AnimationFrame))

            # And loop for all but the Basis shapekey.
            row = []
            for AnimationShapes in range(0, len(ShapeKeyName2)):
                MyData = MyShapekeys[ShapeKeyName2[AnimationShapes]].value
                row = row + [float("%0.4f" % (MyData))]

            Animation_Output.write(str(list(row)) + "\n")
            #print (list(row))

        Animation_Output.close()

        #print("---------------------------")
        print("Done writing Animation List")
        print("---------------------------")


# ------------------------------------ UI area  ------------------------------------



class EXPORT_OT_tools_diffmap_exporter(bpy.types.Operator):
    '''Import from DXF file format (.dxf)'''
    bl_idname = "object.export_diffmaps_from_shapes"
    bl_description = 'Export to MetaMorph file format'
    bl_label = "Export Diff" +' v.'+ __version__
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_context = "data"

    filename_ext = ".tga"
    filter_glob = StringProperty(default="*.tga", options={'HIDDEN'})

    filepath = StringProperty(name="File Path", description="Filepath used for exporting diffmap files", maxlen= 1024, default= "", subtype='FILE_PATH')
    filename = bpy.props.StringProperty(name="File Name", description="Name of the file",)
    name = StringProperty( name="Name", description="Name for the file (without tga extension please)", maxlen = 512, default = "Name")

    #try:
    #    bpy.context.active_object.name
    #except NameError:
    #    name = StringProperty( name="Name", description="Name for the file (without tga extension please)", maxlen = 512, default = "Name")
    #else:
    #    name = StringProperty( name="Name", description="Name for the file (without tga extension please)", maxlen = 512, default = bpy.context.active_object.name)

    width = IntProperty( name="Width", description="Width of image to export", default = 256, min= 1, max=65535)
    height = IntProperty( name="Height", description="Height of image to export", default = 256, min= 1, max=65535)
    shapeson = BoolProperty( name="Export ShapeKeys", description="Save shapekeys as TGA images", default = True)
    animationson = BoolProperty( name="Export Animation", description="Save shapekeys animation", default = True)
    margin = IntProperty( name="Edge Margin", description="sets outside margin around UV edges", default = 10, min= 0, max=64)


    ##### DRAW #####
    def draw(self, context):
        layout = self.layout

        filepath = os.path.dirname( self.filepath )

        os.path.join(filepath)

        row = layout.row()

        row = layout.row()
        row.prop(self, "name")

        col = layout.column(align=True)
        col.prop(self, "width")
        col.prop(self, "height")
        col.prop(self, "margin")

        me = context.active_object.data
        col = layout.column(align=False)
        col.template_list( me, "uv_textures", me.uv_textures, "active_index", rows=2)

        col = layout.column(align=False)
        col.prop(self, "shapeson")
        col.prop(self, "animationson")

    def execute(self, context):
        #name = context.active_object.name

        start = time.time()
        main(self, context)
        print ("Time elapsed:", time.time() - start, "seconds.")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        try:
            bpy.context.active_object.name
        except NameError:
            pass
        else:
            self.name = bpy.context.active_object.name


        return {'RUNNING_MODAL'}

def main():
    instance = CMskExportDiffmap()
    instance.execute(bpy.context)

if __name__ == '__main__':
    main()