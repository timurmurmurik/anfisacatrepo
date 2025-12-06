import math
import bpy
import bmesh
from mathutils import Vector


def principal_axis(coords):
    if not coords:
        return Vector((1.0, 0.0))
    mean = sum(coords, Vector()) / len(coords)
    centered = [c - mean for c in coords]
    cov_x = sum(c.x * c.x for c in centered)
    cov_y = sum(c.y * c.y for c in centered)
    cov_xy = sum(c.x * c.y for c in centered)
    if cov_xy == 0 and cov_x == cov_y:
        return Vector((1.0, 0.0))
    angle = 0.5 * math.atan2(2 * cov_xy, cov_x - cov_y)
    return Vector((math.cos(angle), math.sin(angle)))


class PRIMEFORM_OT_uv_flow_align(bpy.types.Operator):
    """Align UV islands to their dominant edge flow for painter-friendly gradients"""

    bl_idname = "primeform.uv_flow"
    bl_label = "Flow Align UVs"
    bl_options = {"REGISTER", "UNDO"}

    uniform_scale: bpy.props.BoolProperty(
        name="Uniform Scale",
        default=True,
        description="Normalize island scale after alignment",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and obj.mode == "EDIT"

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        islands = bmesh.ops.uv_separate_islands(bm, seams=False)
        island_faces = islands.get("islands", [])

        for faces in island_faces:
            coords = []
            for f in faces:
                for loop in f.loops:
                    coords.append(loop[uv_layer].uv.copy())
            axis = principal_axis(coords)
            perp = Vector((-axis.y, axis.x))
            origin = coords[0] if coords else Vector()

            for f in faces:
                for loop in f.loops:
                    uv = loop[uv_layer].uv
                    rotated = Vector((uv - origin).dot(axis), (uv - origin).dot(perp))
                    loop[uv_layer].uv = rotated

            if self.uniform_scale:
                uvs = [loop[uv_layer].uv for f in faces for loop in f.loops]
                if not uvs:
                    continue
                min_uv = Vector((min(u.x for u in uvs), min(u.y for u in uvs)))
                max_uv = Vector((max(u.x for u in uvs), max(u.y for u in uvs)))
                size = max((max_uv - min_uv).length, 1e-5)
                for f in faces:
                    for loop in f.loops:
                        loop[uv_layer].uv = (loop[uv_layer].uv - min_uv) / size

        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}
