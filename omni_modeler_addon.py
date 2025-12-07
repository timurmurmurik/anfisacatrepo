# coding: utf-8
"""
Omni Modeler Blender Add-on
===========================

A modeling assistant that can rapidly scaffold vehicles, animals, and human figures.
This file is self contained and can be installed in Blender via the Add-ons preferences.
"""

bl_info = {
    "name": "Omni Modeler",
    "author": "OpenAI Agent",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Omni Modeler",
    "description": "Rapidly blocks out cars, animals, and human figures with smart defaults.",
    "warning": "",
    "category": "Object",
}

import bmesh
import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, PointerProperty, StringProperty


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def ensure_collection(name: str) -> bpy.types.Collection:
    """Create or fetch a collection by name and link it to the scene."""
    scene = bpy.context.scene
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
    return collection


def link_object(obj: bpy.types.Object, collection_name: str) -> None:
    """Link an object to a collection, unlinking it from others if needed."""
    collection = ensure_collection(collection_name)
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)


def focus_object(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def add_mirror_and_subsurf(obj: bpy.types.Object, use_mirror: bool, use_subsurf: bool) -> None:
    if use_mirror:
        mirror = obj.modifiers.new(name="OmniMirror", type="MIRROR")
        mirror.use_clip = True
    if use_subsurf:
        subdiv = obj.modifiers.new(name="OmniSubsurf", type="SUBSURF")
        subdiv.levels = 2
        subdiv.render_levels = 2


def set_smooth(obj: bpy.types.Object) -> None:
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = 1.134464


def mesh_from_bmesh(name: str, bm: bmesh.types.BMesh) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    return obj


# -----------------------------------------------------------------------------
# Shape builders
# -----------------------------------------------------------------------------

def build_car_base(scale: float) -> bpy.types.Object:
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=(2.4 * scale, 1.1 * scale, 0.6 * scale))

    top_faces = [f for f in bm.faces if all(v.co.z > 0 for v in f.verts)]
    bmesh.ops.extrude_face_region(bm, geom=top_faces)
    bmesh.ops.translate(
        bm,
        verts=[v for f in top_faces for v in f.verts],
        vec=(0, 0, 0.5 * scale),
    )
    bmesh.ops.scale(
        bm,
        verts=[v for f in top_faces for v in f.verts],
        vec=(0.8, 0.9, 1.0),
    )

    flank_faces = [f for f in bm.faces if any(v.co.x > 1.8 * scale for v in f.verts)]
    if flank_faces:
        bmesh.ops.inset_region(bm, faces=flank_faces, thickness=0.12 * scale, depth=0.05 * scale)

    obj = mesh_from_bmesh("OmniCar", bm)
    obj.location = (0, 0, scale * 0.6)
    return obj


def build_quadruped_base(scale: float) -> bpy.types.Object:
    bm = bmesh.new()
    body = bmesh.ops.create_cube(bm, size=1.6 * scale)["verts"]
    bmesh.ops.scale(bm, verts=body, vec=(1.6, 0.8, 0.6))

    head_geom = bmesh.ops.extrude_face_region(bm, geom=[f for f in bm.faces if f.normal.x > 0.5])
    head_verts = [elem for elem in head_geom["geom"] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=head_verts, vec=(1.1 * scale, 0, 0.1 * scale))
    bmesh.ops.scale(bm, verts=head_verts, vec=(0.6, 0.6, 0.6))

    neck_geom = bmesh.ops.extrude_face_region(bm, geom=[f for f in bm.faces if f.normal.x > 0.2])
    neck_verts = [elem for elem in neck_geom["geom"] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=neck_verts, vec=(0.3 * scale, 0, 0.2 * scale))
    bmesh.ops.scale(bm, verts=neck_verts, vec=(0.8, 0.7, 0.7))

    for side in (-0.45, 0.45):
        for depth in (-0.25, 0.25):
            leg_faces = [
                f
                for f in bm.faces
                if any((v.co.x < -0.4 * scale) and (v.co.y > depth) and (v.co.y < depth + 0.4) for v in f.verts)
            ]
            if leg_faces:
                leg = bmesh.ops.extrude_face_region(bm, geom=leg_faces)
                leg_verts = [elem for elem in leg["geom"] if isinstance(elem, bmesh.types.BMVert)]
                bmesh.ops.translate(bm, verts=leg_verts, vec=(0, side * scale, -0.9 * scale))
                bmesh.ops.scale(bm, verts=leg_verts, vec=(0.6, 0.6, 1.1))

    obj = mesh_from_bmesh("OmniQuadruped", bm)
    obj.location = (0, 0, scale)
    return obj


def build_human_base(scale: float) -> bpy.types.Object:
    bm = bmesh.new()
    spine = bmesh.ops.create_cube(bm, size=1.0 * scale)["verts"]
    bmesh.ops.scale(bm, verts=spine, vec=(0.6, 0.4, 1.6))

    head_geom = bmesh.ops.extrude_face_region(bm, geom=[f for f in bm.faces if f.normal.z > 0.9])
    head_verts = [elem for elem in head_geom["geom"] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=head_verts, vec=(0, 0, 0.9 * scale))
    bmesh.ops.scale(bm, verts=head_verts, vec=(0.6, 0.6, 0.6))

    shoulder_faces = [
        f for f in bm.faces if f.normal.y != 0 and abs(f.calc_center_median().z - 0.8 * scale) < 0.6
    ]
    arms_geom = bmesh.ops.extrude_face_region(bm, geom=shoulder_faces)
    arms_verts = [elem for elem in arms_geom["geom"] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=arms_verts, vec=(0, 0, -0.2 * scale))
    bmesh.ops.scale(bm, verts=arms_verts, vec=(0.8, 1.9, 0.6))

    waist_faces = [f for f in bm.faces if f.normal.z < -0.9]
    waist_geom = bmesh.ops.extrude_face_region(bm, geom=waist_faces)
    waist_verts = [elem for elem in waist_geom["geom"] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=waist_verts, vec=(0, 0, -0.4 * scale))
    bmesh.ops.scale(bm, verts=waist_verts, vec=(0.7, 0.7, 1.0))

    for side in (-0.4, 0.4):
        hip_faces = [f for f in bm.faces if any((v.co.x > 0.1 * scale) and (abs(v.co.y) > 0.1) for v in f.verts)]
        if hip_faces:
            leg = bmesh.ops.extrude_face_region(bm, geom=hip_faces)
            leg_verts = [elem for elem in leg["geom"] if isinstance(elem, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=leg_verts, vec=(side * scale, 0, -1.4 * scale))
            bmesh.ops.scale(bm, verts=leg_verts, vec=(0.7, 0.7, 1.2))

    obj = mesh_from_bmesh("OmniHuman", bm)
    obj.location = (0, 0, scale)
    return obj


# -----------------------------------------------------------------------------
# Properties
# -----------------------------------------------------------------------------


class OmniModelerSettings(PropertyGroup):
    collection_name: StringProperty(
        name="Collection",
        description="Collection where generated meshes will be placed",
        default="OmniModeler",
    )
    scale: FloatProperty(
        name="Scale",
        description="Overall size multiplier for generated meshes",
        default=1.0,
        min=0.1,
        max=10.0,
    )
    use_mirror: BoolProperty(
        name="Mirror",
        description="Add a Mirror modifier aligned to X",
        default=True,
    )
    use_subsurf: BoolProperty(
        name="Subsurf",
        description="Add a subdivision modifier for smoothing",
        default=True,
    )
    auto_smooth: BoolProperty(
        name="Auto Smooth",
        description="Enable smooth shading with auto-smooth angle",
        default=True,
    )


# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------


class OMNI_OT_create_car(Operator):
    bl_idname = "omni_modeler.create_car"
    bl_label = "Create Car Base"
    bl_description = "Create a blockout for a vehicle body with wheel arches and roof"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.omni_modeler
        obj = build_car_base(settings.scale)
        link_object(obj, settings.collection_name)
        focus_object(obj)
        add_mirror_and_subsurf(obj, settings.use_mirror, settings.use_subsurf)
        if settings.auto_smooth:
            set_smooth(obj)
        return {"FINISHED"}


class OMNI_OT_create_quadruped(Operator):
    bl_idname = "omni_modeler.create_quadruped"
    bl_label = "Create Quadruped"
    bl_description = "Create a four-legged creature blockout with neck and head"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.omni_modeler
        obj = build_quadruped_base(settings.scale)
        link_object(obj, settings.collection_name)
        focus_object(obj)
        add_mirror_and_subsurf(obj, settings.use_mirror, settings.use_subsurf)
        if settings.auto_smooth:
            set_smooth(obj)
        return {"FINISHED"}


class OMNI_OT_create_human(Operator):
    bl_idname = "omni_modeler.create_human"
    bl_label = "Create Human"
    bl_description = "Create a mannequin-style human blockout ready for sculpting"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.omni_modeler
        obj = build_human_base(settings.scale)
        link_object(obj, settings.collection_name)
        focus_object(obj)
        add_mirror_and_subsurf(obj, settings.use_mirror, settings.use_subsurf)
        if settings.auto_smooth:
            set_smooth(obj)
        return {"FINISHED"}


# -----------------------------------------------------------------------------
# Panels
# -----------------------------------------------------------------------------


class OMNI_PT_panel(Panel):
    bl_label = "Omni Modeler"
    bl_idname = "OMNI_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Omni Modeler"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.omni_modeler

        box = layout.box()
        box.label(text="Output")
        box.prop(settings, "collection_name")
        box.prop(settings, "scale")

        box2 = layout.box()
        box2.label(text="Mesh Quality")
        box2.prop(settings, "use_mirror")
        box2.prop(settings, "use_subsurf")
        box2.prop(settings, "auto_smooth")

        layout.label(text="Blockouts")
        row = layout.row()
        row.operator(OMNI_OT_create_car.bl_idname, icon="AUTO")
        row = layout.row()
        row.operator(OMNI_OT_create_quadruped.bl_idname, icon="ARMATURE_DATA")
        row = layout.row()
        row.operator(OMNI_OT_create_human.bl_idname, icon="OUTLINER_OB_ARMATURE")


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------


classes = (
    OmniModelerSettings,
    OMNI_OT_create_car,
    OMNI_OT_create_quadruped,
    OMNI_OT_create_human,
    OMNI_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.omni_modeler = PointerProperty(type=OmniModelerSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.omni_modeler


if __name__ == "__main__":
    register()
