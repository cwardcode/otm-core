from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_from_spec(spec) -> ModuleType:
    if spec is None or spec.loader is None:
        raise ImportError("Unable to locate a PostgreSQL driver")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_psycopg2_real() -> ModuleType:
    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parent
    for entry in sys.path:
        if not entry:
            continue
        entry_path = Path(entry).resolve()
        if entry_path in {package_dir, project_root}:
            continue
        spec = importlib.machinery.PathFinder.find_spec(
            "psycopg2", [str(entry_path)])
        if spec is None:
            continue
        origin = getattr(spec, "origin", None)
        if origin and Path(origin).resolve() == Path(__file__).resolve():
            continue
        return _load_from_spec(spec)
    raise ImportError("psycopg2 is not installed")


def _load_psycopg3() -> ModuleType:
    try:
        from psycopg import connect as connect
        from psycopg.types import hstore as hstore
    except ImportError as exc:
        raise ImportError("psycopg 3 is not installed") from exc

    module = ModuleType("psycopg2")
    module.connect = connect
    module.extras = type(
        "Extras", (), {
            "register_hstore": staticmethod(
                hstore.register_hstore)})
    return module


def _load_impl() -> ModuleType:
    try:
        return _load_psycopg2_real()
    except ImportError:
        return _load_psycopg3()


_impl = _load_impl()

if not hasattr(_impl, "extras"):
    class _CompatExtras:
        @staticmethod
        def register_hstore(cursor, globally=False, unicode=False):
            return None

    _impl.extras = _CompatExtras()

for name in dir(_impl):
    if name.startswith("__") and name.endswith("__"):
        continue
    globals()[name] = getattr(_impl, name)

__all__ = getattr(_impl, "__all__", []) or [
    name for name in globals() if not name.startswith("_")]
