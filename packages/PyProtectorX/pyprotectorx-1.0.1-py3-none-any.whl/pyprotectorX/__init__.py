# -*- coding: utf-8 -*-
"""
Auto-loader for the PyProtector binary module.
"""

import importlib.util
import os

__all__ = []

try:
    from . import PyProtectorX as _lib  # type: ignore
except Exception:
    _lib = None
    pkg_dir = os.path.dirname(__file__)
    candidates = [f for f in os.listdir(pkg_dir) if f.startswith("PyProtectorX") and f.endswith(".so")]
    if candidates:
        so_path = os.path.join(pkg_dir, candidates[0])
        spec = importlib.util.spec_from_file_location("pyprotectorX._binary", so_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        _lib = module
    else:
        raise ImportError("Cannot find PyProtector binary module")

for name in dir(_lib):
    if not name.startswith("_"):
        globals()[name] = getattr(_lib, name)
        __all__.append(name)
