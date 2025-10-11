import unittest
from pathlib import Path
from reposmith.config_utils import load_or_create_config


class TestConfigUtils(unittest.TestCase):
    def setUp(self):
        self.root = Path("tests/tmp")
        self.root.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # تنظيف بعد الاختبار
        for f in self.root.glob("*"):
            f.unlink()
        self.root.rmdir()

    def test_creates_default_config_when_missing(self):
        # ينشئ config جديد إذا لم يكن موجودًا
        cfg = load_or_create_config(self.root)
        p = self.root / "setup-config.json"
        self.assertTrue(p.exists())
        self.assertIsInstance(cfg, dict)
        self.assertIn("project_name", cfg)
        self.assertIn("license", cfg)
