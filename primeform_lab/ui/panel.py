import bpy


class VIEW3D_PT_primeform_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PrimeForm"
    bl_label = "PrimeForm Lab"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Concept Blockout")
        col.operator("primeform.block_scatter", icon="MOD_ARRAY")

        col.separator()
        col.label(text="Relax & Flow")
        col.operator("primeform.surface_relax", icon="MOD_SMOOTH")
        col.operator("primeform.uv_flow", icon="GROUP_UVS")


def register(classes):
    classes.append(VIEW3D_PT_primeform_panel)


def unregister(classes):
    if VIEW3D_PT_primeform_panel in classes:
        classes.remove(VIEW3D_PT_primeform_panel)
