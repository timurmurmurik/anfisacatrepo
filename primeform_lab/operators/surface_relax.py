import bpy
import bmesh
from mathutils import Vector


class PRIMEFORM_OT_surface_relax(bpy.types.Operator):
    """Relax selected vertices while preserving silhouette and anchors"""

    bl_idname = "primeform.surface_relax"
    bl_label = "Silhouette-Safe Relax"
    bl_options = {"REGISTER", "UNDO"}

    iterations: bpy.props.IntProperty(name="Iterations", default=8, min=1, max=100)
    intensity: bpy.props.FloatProperty(
        name="Intensity", default=0.35, min=0.0, max=1.0, description="Blend factor per step"
    )
    pin_border: bpy.props.BoolProperty(
        name="Pin Border",
        default=True,
        description="Keep boundary vertices fixed to preserve silhouette",
    )
    volume_hold: bpy.props.FloatProperty(
        name="Volume Hold",
        default=0.35,
        min=0.0,
        max=1.0,
        description="Blend the relaxed result toward the original position to reduce shrinkage",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and obj.mode == "EDIT"

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active

        original_positions = {v.index: v.co.copy() for v in bm.verts}

        for _ in range(self.iterations):
            new_positions = {}
            for v in bm.verts:
                if not v.select:
                    continue
                if self.pin_border and v.is_boundary:
                    continue

                neighbors = [e.other_vert(v) for e in v.link_edges]
                if not neighbors:
                    continue
                avg = sum((n.co for n in neighbors), Vector()) / len(neighbors)
                new_positions[v.index] = v.co.lerp(avg, self.intensity)

            for idx, new_co in new_positions.items():
                original = original_positions[idx]
                target = new_co.lerp(original, self.volume_hold)
                bm.verts[idx].co = target

        if uv_layer:
            for face in bm.faces:
                for loop in face.loops:
                    loop[uv_layer].pin_uv = True

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        return {"FINISHED"}
