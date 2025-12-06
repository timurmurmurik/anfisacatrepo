from .panel import VIEW3D_PT_primeform_panel

__all__ = [
    "VIEW3D_PT_primeform_panel",
]


def register(classes):
    classes.append(VIEW3D_PT_primeform_panel)


def unregister(classes):
    if VIEW3D_PT_primeform_panel in classes:
        classes.remove(VIEW3D_PT_primeform_panel)
