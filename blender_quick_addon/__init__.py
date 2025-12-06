"""
A Blender 3D addon that provides a panel in the 3D Viewport's sidebar to
quickly create a beveled cube with custom dimensions and subdivision settings.

This module can be installed as an addon zip archive in Blender. The `bl_info`
structure below exposes metadata so Blender can present the addon in the
Preferences dialog.
"""

bl_info = {
    "name": "Quick Beveled Cube",
    "author": "ChatGPT",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Create Tab",
    "description": "Adds a panel for creating customizable beveled cubes",
    "category": "Add Mesh",
}

import bpy
import bmesh
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty


class QuickBeveledCubeProperties(PropertyGroup):
    width: FloatProperty(
        name="Width",
        description="Cube width along the X axis",
        default=2.0,
        min=0.01,
        soft_max=10.0,
        unit='LENGTH',
    )
    depth: FloatProperty(
        name="Depth",
        description="Cube depth along the Y axis",
        default=2.0,
        min=0.01,
        soft_max=10.0,
        unit='LENGTH',
    )
    height: FloatProperty(
        name="Height",
        description="Cube height along the Z axis",
        default=2.0,
        min=0.01,
        soft_max=10.0,
        unit='LENGTH',
    )
    bevel_amount: FloatProperty(
        name="Bevel Amount",
        description="Bevel width applied to cube edges",
        default=0.1,
        min=0.0,
        soft_max=2.0,
        unit='LENGTH',
    )
    bevel_segments: IntProperty(
        name="Bevel Segments",
        description="Number of segments used to smooth the bevel",
        default=2,
        min=1,
        soft_max=12,
    )
    smooth_shading: BoolProperty(
        name="Smooth Shading",
        description="Apply smooth shading to the generated cube",
        default=True,
    )


class OBJECT_OT_add_quick_beveled_cube(Operator):
    """Create a beveled cube with the selected dimensions"""

    bl_idname = "mesh.add_quick_beveled_cube"
    bl_label = "Add Quick Beveled Cube"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.quick_beveled_cube

        mesh = bpy.data.meshes.new(name="QuickBeveledCube")
        obj = bpy.data.objects.new(name="QuickBeveledCube", object_data=mesh)

        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj

        bm = bmesh.new()
        bmesh.ops.create_cube(
            bm,
            size=1.0,
        )

        # Scale cube to desired dimensions.
        bmesh.ops.scale(
            bm,
            vec=(settings.width, settings.depth, settings.height),
            verts=bm.verts,
        )

        if settings.bevel_amount > 0:
            bmesh.ops.bevel(
                bm,
                geom=bm.edges[:],
                offset=settings.bevel_amount,
                segments=settings.bevel_segments,
                profile=0.7,
                affect='EDGES',
                clamp_overlap=True,
            )

        bm.to_mesh(mesh)
        bm.free()

        if settings.smooth_shading:
            mesh.use_auto_smooth = True
            for poly in mesh.polygons:
                poly.use_smooth = True

        return {'FINISHED'}


class VIEW3D_PT_quick_beveled_cube(Panel):
    """Panel for quickly adding beveled cubes"""

    bl_label = "Quick Beveled Cube"
    bl_idname = "VIEW3D_PT_quick_beveled_cube"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Create'

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.quick_beveled_cube

        col = layout.column(align=True)
        col.prop(settings, "width")
        col.prop(settings, "depth")
        col.prop(settings, "height")

        col.separator()
        col.prop(settings, "bevel_amount")
        col.prop(settings, "bevel_segments")
        col.prop(settings, "smooth_shading")

        layout.operator(OBJECT_OT_add_quick_beveled_cube.bl_idname, icon='MESH_CUBE')


def register():
    bpy.utils.register_class(QuickBeveledCubeProperties)
    bpy.utils.register_class(OBJECT_OT_add_quick_beveled_cube)
    bpy.utils.register_class(VIEW3D_PT_quick_beveled_cube)
    bpy.types.Scene.quick_beveled_cube = PointerProperty(type=QuickBeveledCubeProperties)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_quick_beveled_cube)
    bpy.utils.unregister_class(OBJECT_OT_add_quick_beveled_cube)
    bpy.utils.unregister_class(QuickBeveledCubeProperties)
    del bpy.types.Scene.quick_beveled_cube


if __name__ == "__main__":
    register()
