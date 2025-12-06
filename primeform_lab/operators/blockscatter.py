import random
import math
import bpy
from mathutils import Vector, Matrix


class PRIMEFORM_OT_block_scatter(bpy.types.Operator):
    """Generate a design blockout made of responsive, golden-ratio-biased chunks"""

    bl_idname = "primeform.block_scatter"
    bl_label = "Generative Block Scatter"
    bl_options = {"REGISTER", "UNDO"}

    count: bpy.props.IntProperty(
        name="Chunks",
        default=8,
        min=1,
        max=200,
        description="How many building blocks to generate",
    )
    seed: bpy.props.IntProperty(name="Seed", default=1, min=0, description="Random seed")
    base_scale: bpy.props.FloatVectorProperty(
        name="Base XYZ",
        default=(1.2, 0.8, 0.6),
        subtype="XYZ",
        description="Average size of blocks (XYZ)",
    )
    spread: bpy.props.FloatVectorProperty(
        name="Spread",
        default=(3.0, 3.0, 1.5),
        subtype="XYZ",
        description="Overall footprint of the cluster",
    )
    arc_bias: bpy.props.FloatProperty(
        name="Arc Bias",
        default=0.2,
        min=0.0,
        max=1.0,
        description="Bend the scatter around the view direction for quick silhouettes",
    )

    def execute(self, context):
        random.seed(self.seed)
        view_rot = context.region_data.view_rotation if context.region_data else Matrix.Identity(3)
        parent = bpy.data.objects.new("PrimeForm_Blockout", None)
        context.collection.objects.link(parent)

        for i in range(self.count):
            size_variation = Vector(
                (
                    self.base_scale[0] * random.uniform(0.5, 1.5),
                    self.base_scale[1] * random.uniform(0.5, 1.3),
                    self.base_scale[2] * random.uniform(0.4, 1.4),
                )
            )
            pos_noise = Vector(
                (
                    (random.random() - 0.5) * self.spread[0],
                    (random.random() - 0.5) * self.spread[1],
                    (random.random() - 0.5) * self.spread[2],
                )
            )

            arc_angle = self.arc_bias * math.sin(i / max(1, self.count - 1) * math.pi)
            arc_offset = Vector((math.sin(arc_angle), math.cos(arc_angle), 0.0)) * 0.5 * self.spread[0]

            loc = pos_noise + arc_offset

            # Build a dedicated mesh object so Blender registers it as a mesh from the start
            bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, location=(0, 0, 0))
            temp_obj = context.active_object
            temp_mesh = temp_obj.data.copy()
            bpy.data.objects.remove(temp_obj, do_unlink=True)

            cube_mesh = bpy.data.meshes.new(f"PrimeBlock_{i:02d}_Mesh")
            cube_mesh.from_mesh(temp_mesh)
            bpy.data.meshes.remove(temp_mesh)

            cube = bpy.data.objects.new(f"PrimeBlock_{i:02d}", cube_mesh)
            bpy.context.collection.objects.link(cube)
            cube.parent = parent

            cube.scale = size_variation
            cube.location = view_rot @ loc if self.arc_bias else loc
            cube.rotation_euler = (
                random.uniform(-0.2, 0.2),
                random.uniform(-0.2, 0.2),
                random.uniform(-math.pi, math.pi),
            )

        return {"FINISHED"}
