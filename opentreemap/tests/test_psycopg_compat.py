import importlib
import pathlib
import sys
import unittest


class PsycopgCompatTests(unittest.TestCase):
    def test_import_psycopg2_uses_project_shim(self):
        project_root = pathlib.Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        sys.modules.pop("psycopg2", None)
        module = importlib.import_module("psycopg2")

        self.assertTrue(pathlib.Path(module.__file__).resolve().exists())
        self.assertTrue(callable(getattr(module, "connect", None)))
        self.assertTrue(hasattr(module, "extras"))


if __name__ == "__main__":
    unittest.main()
