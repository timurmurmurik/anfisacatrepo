"""
PrimeForm Lab Blender add-on shim.

This repository is packaged with the add-on code under the `primeform_lab`
package. When users install the GitHub ZIP directly, Blender expects the
top-level folder to expose `bl_info`, `register`, and `unregister`. This
shim forwards those to the real implementation so that ZIP installs work
without manual repackaging.
"""
from primeform_lab import bl_info as _bl_info
from primeform_lab import register as _register
from primeform_lab import unregister as _unregister

bl_info = _bl_info


def register():
    _register()


def unregister():
    _unregister()


if __name__ == "__main__":
    register()
