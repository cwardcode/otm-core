from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_from_path(path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location("psycopg2_driver", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load PostgreSQL driver from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_driver() -> ModuleType:
    self_dir = Path(__file__).resolve().parent
    for entry in sys.path:
        if not entry:
            continue
        entry_path = Path(entry).resolve()
        if entry_path == self_dir:
            continue
        spec = importlib.machinery.PathFinder.find_spec(
            "psycopg2", [str(entry_path)])
        if spec is None:
            continue
        origin = getattr(spec, "origin", None)
        if origin is None:
            continue
        origin_path = Path(origin).resolve()
        if origin_path == Path(__file__).resolve():
            continue
        return _load_from_path(str(origin_path))

    try:
        return importlib.import_module("psycopg")
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Neither psycopg2 nor psycopg is installed") from exc


def _install(module: ModuleType) -> None:
    for name in dir(module):
        if name.startswith("__") and name.endswith("__"):
            continue
        globals()[name] = getattr(module, name)

    globals()["__file__"] = __file__
    globals()["__path__"] = [str(Path(__file__).resolve().parent)]

    try:
        extras = importlib.import_module("psycopg2_driver.extras")
    except Exception:  # pragma: no cover - optional submodule
        extras = None

    if extras is not None:
        globals()["extras"] = extras
        sys.modules["psycopg2.extras"] = extras


_install(_load_driver())
