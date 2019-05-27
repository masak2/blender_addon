# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntVectorProperty,
                       FloatProperty,
                       )
class CMskExportColorLayoutPng(bpy.types.Operator):
##class CMskExportBoneLengthInfo():
    bl_idname = "masak.msk_io_export_color_layout_png"
    bl_label = "msk_io_export_color_layout_png"
    bl_description = "Export ID MAP as png"
    #bl_context = "objectmode"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    check_existing = BoolProperty(
            name="Check Existing",
            description="Check and warn on overwriting existing files",
            default=True,
            options={'HIDDEN'},
            )
    export_all = BoolProperty(
            name="All UVs",
            description="Export all UVs in this mesh (not just visible ones)",
            default=False,
            )
    modified = BoolProperty(
            name="Modified",
            description="Exports UVs from the modified mesh",
            default=False,
            )
    mode = EnumProperty(
            items=(('PNG', "PNG Image (.png)",
                    "Export the Color ID layout to a bitmap image"),
                   ),
            name="Format",
            description="File format to export the Color ID layout to",
            default='PNG',
            )
    size = IntVectorProperty(
            size=2,
            default=(1024, 1024),
            min=8, max=32768,
            description="Dimensions of the exported file",
            )
    tessellated = BoolProperty(
            name="Tessellated UVs",
            description="Export tessellated UVs instead of polygons ones",
            default=False,
            options={'HIDDEN'},  # As not working currently :/
            )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and obj.data.uv_textures)

    def _space_image(self, context):
        space_data = context.space_data
        if isinstance(space_data, bpy.types.SpaceImageEditor):
            return space_data
        else:
            return None

    def _image_size(self, context, default_width=1024, default_height=1024):
        # fallback if not in image context.
        image_width, image_height = default_width, default_height

        space_data = self._space_image(context)
        if space_data:
            image = space_data.image
            if image:
                width, height = tuple(context.space_data.image.size)
                # in case no data is found.
                if width and height:
                    image_width, image_height = width, height

        return image_width, image_height

    def _face_uv_iter(self, context, mesh, tessellated):
        uv_layer = mesh.uv_layers.active.data
        polys = mesh.polygons

        if not self.export_all:
            uv_tex = mesh.uv_textures.active.data
            local_image = Ellipsis

            if context.tool_settings.show_uv_local_view:
                space_data = self._space_image(context)
                if space_data:
                    local_image = space_data.image

            for i, p in enumerate(polys):
                # context checks
                if polys[i].select and local_image in {Ellipsis,
                                                       uv_tex[i].image}:
                    start = p.loop_start
                    end = start + p.loop_total
                    uvs = tuple((uv.uv[0], uv.uv[1])
                                for uv in uv_layer[start:end])

                    # just write what we see.
                    yield (i, uvs)
        else:
            # all, simple
            for i, p in enumerate(polys):
                start = p.loop_start
                end = start + p.loop_total
                uvs = tuple((uv.uv[0], uv.uv[1]) for uv in uv_layer[start:end])
                yield (i, uvs)

    def execute(self, context):

        obj = context.active_object
        is_editmode = (obj.mode == 'EDIT')
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        mode = self.mode

        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, "." + mode.lower())
      # filepath = bpy.path.ensure_ext(filepath, ".png")
        file = open(filepath, "w")
        fw = file.write

        if mode == 'PNG':
            #from . import export_colour_layout_png
            #func = export_colour_layout_png.write
            func = self.write


        if self.modified:
            mesh = obj.to_mesh(context.scene, True, 'PREVIEW')
        else:
            mesh = obj.data

        func(fw, obj, mesh, self.size[0], self.size[1],
             lambda: self._face_uv_iter(context, mesh, self.tessellated))

        if self.modified:
            bpy.data.meshes.remove(mesh)

        if is_editmode:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        file.close()

        return {'FINISHED'}

    def check(self, context):
        filepath = bpy.path.ensure_ext(self.filepath, "." + self.mode.lower())
     #  filepath = bpy.path.ensure_ext(self.filepath, ".png")
        if filepath != self.filepath:
            self.filepath = filepath
            return True
        else:
            return False

    def invoke(self, context, event):
        import os
        self.size = self._image_size(context)
        self.filepath = os.path.splitext(bpy.data.filepath)[0]
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def write(self, fw, obj_source, mesh_source, image_width, image_height, face_iter_func):


        try:
            assert obj_source.vertex_groups
            assert mesh_source.vertex_colors
        
        except AssertionError:
            bpy.ops.error.message('INVOKE_DEFAULT', 
                    type = "Error",
                    message = 'you need at least one vertex group and one color group')
            return

        filepath = fw.__self__.name
        fw.__self__.close()

        #material_solids = [bpy.data.materials.new("uv_temp_solid")
        #                   for i in range(max(1, len(mesh_source.materials)))]

        # count the number of specific vertex group
        vgrp_arr = []
        for vgrp in obj_source.vertex_groups:
            print (vgrp.name)
            if vgrp.name.startswith("vc_"):
                vgrp_arr.append(vgrp)
        material_solids = [bpy.data.materials.new("uv_temp_solid")
                           for i in range(max(1, len(vgrp_arr)))]
        

        scene = bpy.data.scenes.new("uv_temp")
        mesh = bpy.data.meshes.new("uv_temp")
        for mat_solid in material_solids:
            mesh.materials.append(mat_solid)

        polys_source = mesh_source.polygons

        # get unique UV's in case there are many overlapping
        # which slow down filling.
        face_hash = {(uvs, polys_source[i].material_index)
                     for i, uvs in face_iter_func()}

        # now set the faces coords and locations
        # build mesh data
        mesh_new_vertices = []
        mesh_new_materials = []
        mesh_new_polys_startloop = []
        mesh_new_polys_totloop = []
        mesh_new_loops_vertices = []

        current_vert = 0

        for uvs, mat_idx in face_hash:
            num_verts = len(uvs)
            dummy = (0.0,) * num_verts
            for uv in uvs:
                mesh_new_vertices += (uv[0], uv[1], 0.0)
            mesh_new_polys_startloop.append(current_vert)
            mesh_new_polys_totloop.append(num_verts)
            mesh_new_loops_vertices += range(current_vert,
                                             current_vert + num_verts)
            mesh_new_materials.append(mat_idx)
            current_vert += num_verts

        mesh.vertices.add(current_vert)
        mesh.loops.add(current_vert)
        mesh.polygons.add(len(mesh_new_polys_startloop))

        mesh.vertices.foreach_set("co", mesh_new_vertices)
        mesh.loops.foreach_set("vertex_index", mesh_new_loops_vertices)
        mesh.polygons.foreach_set("loop_start", mesh_new_polys_startloop)
        mesh.polygons.foreach_set("loop_total", mesh_new_polys_totloop)
        mesh.polygons.foreach_set("material_index", mesh_new_materials)

        mesh.update(calc_edges=True)

        obj_solid = bpy.data.objects.new("uv_temp_solid", mesh)
        base_solid = scene.objects.link(obj_solid)
        base_solid.layers[0] = True


        # place behind the wire
        obj_solid.location = 0, 0, -1

        # setup the camera
        cam = bpy.data.cameras.new("uv_temp")
        cam.type = 'ORTHO'
        cam.ortho_scale = 1.0
        obj_cam = bpy.data.objects.new("uv_temp_cam", cam)
        obj_cam.location = 0.5, 0.5, 1.0
        scene.objects.link(obj_cam)
        scene.camera = obj_cam

        # setup materials
        h_offset = 40
        if len(material_solids) > 9:
            h_offset = 360 / len(material_solids)
        print(h_offset)
        for i, mat_solid in enumerate(material_solids):
            #if mesh_source.materials and mesh_source.materials[i]:
            #    mat_solid.diffuse_color = mesh_source.materials[i].diffuse_color
            col = Color()
            col.h = i*h_offset/255.0
            col.s = 1
            col.v = 1
            mat_solid.diffuse_color = [col.r, col.g, col.b]
            mat_solid.use_shadeless = True
            mat_solid.use_transparency = True
            mat_solid.alpha = 1.0


        # scene render settings
        scene.render.use_raytrace = False
        scene.render.alpha_mode = 'TRANSPARENT'
        scene.render.image_settings.color_mode = 'RGBA'

        scene.render.resolution_x = image_width
        scene.render.resolution_y = image_height
        scene.render.resolution_percentage = 100

        if image_width > image_height:
            scene.render.pixel_aspect_y = image_width / image_height
        elif image_width < image_height:
            scene.render.pixel_aspect_x = image_height / image_width

        scene.frame_start = 1
        scene.frame_end = 1

        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = filepath

        data_context = {"blend_data": bpy.context.blend_data, "scene": scene}
        bpy.ops.render.render(data_context, write_still=True)

        # cleanup
        bpy.data.scenes.remove(scene)
        bpy.data.objects.remove(obj_cam)
        bpy.data.objects.remove(obj_solid)

        bpy.data.cameras.remove(cam)
        bpy.data.meshes.remove(mesh)

        for mat_solid in material_solids:
            bpy.data.materials.remove(mat_solid)
            return{'FINISHED'}

def main():
    instance = CMskExportColorLayoutPng()
    instance.execute(bpy.context)
if __name__ == '__main__':
    main()


