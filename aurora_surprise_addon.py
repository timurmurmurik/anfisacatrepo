"""Aurora Surprise Blender addon.

Creates a luminous aurora portal with dancing sparkles and animated emission.
This addon is meant to be playful and surprising: it builds a shimmering ribbon,
a flock of glowing confetti, and optional lighting in one click.
"""

bl_info = {
    "name": "Aurora Surprise Portal",
    "author": "OpenAI Assistant",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Aurora Surprise",
    "description": "Adds a luminous aurora portal with animated sparkles",
    "category": "Add Mesh",
}

import bpy
from bpy import types
from math import pi
from mathutils import Color


COLLECTION_NAME = "Aurora Surprise"
PORTAL_NAME = "Aurora Portal"
SPARK_EMITTER_NAME = "Aurora Spark Emitter"
SPARK_OBJECT_NAME = "Aurora Spark"
LIGHT_NAME = "Aurora Light"


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def ensure_collection(context):
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        context.scene.collection.children.link(collection)
    elif collection.name not in context.scene.collection.children:
        context.scene.collection.children.link(collection)
    return collection


def link_to_collection(obj, collection):
    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    collection.objects.link(obj)


def ensure_driver(value, expression):
    fcurve = value.driver_add("default_value")
    driver = fcurve.driver
    driver.expression = expression
    return driver


# -----------------------------------------------------------------------------
# Content creation
# -----------------------------------------------------------------------------

def create_portal_mesh(context, radius, thickness, twist):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        abso_major_rad=1.25,
        abso_minor_rad=0.75,
        location=context.scene.cursor.location,
    )
    obj = context.active_object
    obj.name = PORTAL_NAME
    obj.data.name = f"{PORTAL_NAME} Mesh"

    subsurf = obj.modifiers.new(name="Smooth", type="SUBSURF")
    subsurf.levels = 2
    subsurf.render_levels = 3

    solidify = obj.modifiers.new(name="Shell", type="SOLIDIFY")
    solidify.thickness = thickness * 0.5

    deform = obj.modifiers.new(name="Spiral", type="SIMPLE_DEFORM")
    deform.deform_method = 'TWIST'
    deform.angle = pi * twist

    tex = bpy.data.textures.new("AuroraNoise", type='CLOUDS')
    displace = obj.modifiers.new(name="Ripple", type="DISPLACE")
    displace.texture = tex
    displace.strength = thickness * 0.6
    displace.mid_level = 0.25

    bpy.ops.object.shade_smooth()
    return obj


def create_portal_material(color, pulse_speed, brightness):
    mat = bpy.data.materials.new(name="Aurora Emission")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs[0].default_value = (color.r, color.g, color.b, 1.0)
    emission.inputs[1].default_value = brightness

    layer_weight = nodes.new(type="ShaderNodeLayerWeight")
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].color = (color.r, color.g * 0.8, color.b, 1)
    color_ramp.color_ramp.elements[1].color = (1.0, 0.95, 0.8, 1)

    time = nodes.new(type="ShaderNodeValue")
    time.outputs[0].default_value = 0.0
    time.name = "Time Driver"

    math_sine = nodes.new(type="ShaderNodeMath")
    math_sine.operation = 'SINE'

    math_scale = nodes.new(type="ShaderNodeMath")
    math_scale.operation = 'MULTIPLY'
    math_scale.inputs[1].default_value = pulse_speed

    math_offset = nodes.new(type="ShaderNodeMath")
    math_offset.operation = 'ADD'
    math_offset.inputs[1].default_value = brightness

    links.new(layer_weight.outputs['Facing'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
    links.new(time.outputs[0], math_scale.inputs[0])
    links.new(math_scale.outputs[0], math_sine.inputs[0])
    links.new(math_sine.outputs[0], math_offset.inputs[0])
    links.new(math_offset.outputs[0], emission.inputs['Strength'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    ensure_driver(time.outputs[0], "frame / 20.0")
    return mat


def create_spark_emitter(context, radius, color, count, lifetime, collection):
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=radius * 0.95, fill_type='NOTHING')
    emitter = context.active_object
    emitter.name = SPARK_EMITTER_NAME

    particle_settings = bpy.data.particles.new(name="AuroraSparkles")
    particle_settings.count = count
    particle_settings.frame_start = 1
    particle_settings.frame_end = 1
    particle_settings.lifetime = lifetime
    particle_settings.lifetime_random = 0.35
    particle_settings.normal_factor = 0.025
    particle_settings.factor_random = 0.05
    particle_settings.tangent_factor = 0.2
    particle_settings.physics_type = 'NEWTON'
    particle_settings.render_type = 'OBJECT'
    particle_settings.use_rotations = True
    particle_settings.angular_velocity_mode = 'RAND'

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03)
    spark = context.active_object
    spark.name = SPARK_OBJECT_NAME
    spark_mat = bpy.data.materials.new(name="Spark Emission")
    spark_mat.use_nodes = True
    spark_nodes = spark_mat.node_tree.nodes
    spark_links = spark_mat.node_tree.links
    spark_nodes.clear()
    spark_output = spark_nodes.new(type="ShaderNodeOutputMaterial")
    spark_emission = spark_nodes.new(type="ShaderNodeEmission")
    spark_emission.inputs[0].default_value = (color.r, color.g, min(color.b + 0.2, 1.0), 1)
    spark_emission.inputs[1].default_value = 12.0
    spark_links.new(spark_emission.outputs['Emission'], spark_output.inputs['Surface'])
    spark.data.materials.append(spark_mat)

    particle_settings.instance_object = spark
    emitter.modifiers.new(name="AuroraParticles", type='PARTICLE_SYSTEM').particle_system.settings = particle_settings
    emitter.hide_render = True
    emitter.hide_viewport = True

    link_to_collection(emitter, collection)
    link_to_collection(spark, collection)
    return emitter, spark


def setup_light(context, collection, color, energy):
    bpy.ops.object.light_add(type='AREA', radius=1.5, location=(0, 0, 2.0))
    light = context.active_object
    light.name = LIGHT_NAME
    light.data.energy = energy
    light.data.color = (color.r, color.g, color.b)
    link_to_collection(light, collection)
    return light


def clear_previous(collection):
    names_to_remove = {PORTAL_NAME, SPARK_EMITTER_NAME, SPARK_OBJECT_NAME, LIGHT_NAME}
    for obj in list(collection.objects):
        if obj.name in names_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
    for obj in list(bpy.data.objects):
        if obj.users == 0 and obj.name in names_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)


# -----------------------------------------------------------------------------
# Properties and Operators
# -----------------------------------------------------------------------------

class AuroraSettings(types.PropertyGroup):
    portal_radius: bpy.props.FloatProperty(
        name="Portal Radius",
        default=1.5,
        min=0.5,
        max=10.0,
        description="Overall diameter of the glowing ring"
    )
    portal_thickness: bpy.props.FloatProperty(
        name="Ribbon Thickness",
        default=0.15,
        min=0.02,
        max=0.7,
        description="Thickness of the luminous ribbon"
    )
    portal_twist: bpy.props.FloatProperty(
        name="Twist Turns",
        default=0.35,
        min=0.0,
        max=1.5,
        description="How much the portal ribbon twists"
    )
    glow_color: bpy.props.FloatVectorProperty(
        name="Glow Color",
        subtype='COLOR',
        min=0.0,
        max=1.0,
        default=(0.3, 0.8, 1.0),
        description="Hue of the portal and sparkles"
    )
    spark_count: bpy.props.IntProperty(
        name="Spark Count",
        default=420,
        min=10,
        max=5000,
        description="Number of spark particles"
    )
    spark_lifetime: bpy.props.IntProperty(
        name="Spark Lifetime",
        default=120,
        min=10,
        max=800,
        description="Lifetime of each spark particle"
    )
    brightness: bpy.props.FloatProperty(
        name="Glow Intensity",
        default=24.0,
        min=1.0,
        max=100.0,
        description="Base emission power"
    )
    pulse_speed: bpy.props.FloatProperty(
        name="Pulse Speed",
        default=6.0,
        min=0.1,
        max=20.0,
        description="Speed of the breathing animation"
    )
    add_light: bpy.props.BoolProperty(
        name="Add Accent Light",
        default=True,
        description="Add a matching area light"
    )
    light_energy: bpy.props.FloatProperty(
        name="Light Energy",
        default=400.0,
        min=0.0,
        max=3000.0,
        description="Energy for the accent light"
    )


class AURORA_OT_add_portal(types.Operator):
    bl_idname = "mesh.aurora_portal_add"
    bl_label = "Summon Aurora Portal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.aurora_settings
        collection = ensure_collection(context)
        clear_previous(collection)

        color = Color()
        color.r, color.g, color.b = settings.glow_color

        portal_obj = create_portal_mesh(context, settings.portal_radius, settings.portal_thickness, settings.portal_twist)
        mat = create_portal_material(color, settings.pulse_speed, settings.brightness)
        portal_obj.data.materials.append(mat)
        link_to_collection(portal_obj, collection)

        create_spark_emitter(
            context,
            settings.portal_radius,
            color,
            settings.spark_count,
            settings.spark_lifetime,
            collection,
        )

        if settings.add_light:
            setup_light(context, collection, color, settings.light_energy)

        self.report({'INFO'}, "Aurora portal created—press Play to watch it breathe.")
        return {'FINISHED'}


class AURORA_OT_cleanup(types.Operator):
    bl_idname = "mesh.aurora_portal_cleanup"
    bl_label = "Remove Aurora Setup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        collection = ensure_collection(context)
        clear_previous(collection)
        self.report({'INFO'}, "Aurora objects removed.")
        return {'FINISHED'}


class AURORA_PT_panel(types.Panel):
    bl_label = "Aurora Surprise"
    bl_idname = "AURORA_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aurora Surprise'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.aurora_settings

        col = layout.column(align=True)
        col.label(text="Portal")
        col.prop(settings, "portal_radius")
        col.prop(settings, "portal_thickness")
        col.prop(settings, "portal_twist")
        col.prop(settings, "glow_color")

        col.separator()
        col.label(text="Animation & Glow")
        col.prop(settings, "brightness")
        col.prop(settings, "pulse_speed")

        col.separator()
        col.label(text="Sparks")
        col.prop(settings, "spark_count")
        col.prop(settings, "spark_lifetime")

        col.separator()
        col.prop(settings, "add_light")
        if settings.add_light:
            col.prop(settings, "light_energy")

        layout.separator()
        layout.operator(AURORA_OT_add_portal.bl_idname, icon='MOD_PARTICLES')
        layout.operator(AURORA_OT_cleanup.bl_idname, icon='TRASH')


classes = (
    AuroraSettings,
    AURORA_OT_add_portal,
    AURORA_OT_cleanup,
    AURORA_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aurora_settings = bpy.props.PointerProperty(type=AuroraSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.aurora_settings


if __name__ == "__main__":
    register()
