from .blockscatter import PRIMEFORM_OT_block_scatter
from .surface_relax import PRIMEFORM_OT_surface_relax
from .uv_flow import PRIMEFORM_OT_uv_flow_align


__all__ = [
    "PRIMEFORM_OT_block_scatter",
    "PRIMEFORM_OT_surface_relax",
    "PRIMEFORM_OT_uv_flow_align",
]


def register(classes):
    classes.extend([
        PRIMEFORM_OT_block_scatter,
        PRIMEFORM_OT_surface_relax,
        PRIMEFORM_OT_uv_flow_align,
    ])


def unregister(classes):
    for cls in [
        PRIMEFORM_OT_block_scatter,
        PRIMEFORM_OT_surface_relax,
        PRIMEFORM_OT_uv_flow_align,
    ]:
        if cls in classes:
            classes.remove(cls)
