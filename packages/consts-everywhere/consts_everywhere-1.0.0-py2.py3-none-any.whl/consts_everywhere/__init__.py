import sys
import assign_overload
from .consts_everywhere import Const

orig_patch_and_reload_module = assign_overload.patch_and_reload_module

def patch_and_reload_module(module = None, trans = assign_overload.transformer.AssignTransformer):
    if module is None:
        module_name = sys._getframe(1).f_globals["__name__"]
        module = sys.modules[module_name]
    if not hasattr(module, "patched") or not module.patched:
        for name in dict(module.__dict__):
            if type(getattr(module, name)).__name__ == "Const":
                delattr(module, name)
    return orig_patch_and_reload_module(module, trans)

assign_overload.patch_and_reload_module = patch_and_reload_module
