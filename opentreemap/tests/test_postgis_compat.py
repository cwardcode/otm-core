import os
import unittest


class PostGISCompatTests(unittest.TestCase):
    def test_postgis_backend_can_be_imported_when_gdal_is_available(self):
        if os.environ.get("OTM_SKIP_GIS_IMPORT") == "1":
            self.skipTest("GDAL import is disabled in this environment")

        try:
            from django.contrib.gis.db.backends.postgis import base
        except Exception as exc:  # pragma: no cover - environment dependent
            self.fail(f"PostGIS backend import failed: {exc}")

        self.assertTrue(hasattr(base, "DatabaseWrapper"))


if __name__ == "__main__":
    unittest.main()
