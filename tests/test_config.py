import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from novacore import config
from novacore.config import Settings, SettingsError


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "novaos" / "settings.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_defaults_when_no_file(self):
        s = Settings(self.path)
        self.assertEqual(s.get("theme"), "auto")
        self.assertEqual(s.get("dock.position"), "bottom")
        self.assertFalse(self.path.exists())

    def test_persists_across_instances(self):  # spec §13: survive reboot
        s = Settings(self.path)
        s.set("theme", "dark"); s.set("dock.autohide", True); s.set("dock.size", 72)
        s2 = Settings(self.path)
        self.assertEqual(s2.get("theme"), "dark")
        self.assertTrue(s2.get("dock.autohide"))
        self.assertEqual(s2.get("dock.size"), 72)

    def test_rejects_invalid(self):
        s = Settings(self.path)
        bad = [("theme", "purple"), ("nope", 1), ("dock.size", 5), ("dock.size", "big"),
               ("animations", "yes"), ("transparency", 101), ("font_scale", 3.0),
               ("dock.autohide", 1), ("icon_size", True)]
        for k, v in bad:
            with self.assertRaises(SettingsError, msg=f"{k}={v!r}"):
                s.set(k, v)
        self.assertEqual(s.get("theme"), "auto")  # unchanged after failures

    def test_group_is_not_a_setting(self):
        with self.assertRaises(SettingsError):
            Settings(self.path).get("dock")

    def test_int_accepted_for_float(self):
        s = Settings(self.path); s.set("font_scale", 1)
        self.assertEqual(s.get("font_scale"), 1.0)

    def test_corrupt_file_falls_back_and_is_preserved(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json")
        s = Settings(self.path)
        self.assertEqual(s.get("theme"), "auto")
        self.assertIsNotNone(s.load_error)
        self.assertTrue(self.path.with_suffix(".json.corrupt").exists())

    def test_bad_entries_ignored_good_kept(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"theme": "dark", "accent": "pink", "ghost": 1, "dock": {"size": 64, "position": "top"}}))
        s = Settings(self.path)
        self.assertEqual(s.get("theme"), "dark")
        self.assertEqual(s.get("accent"), "violet")      # invalid -> default
        self.assertEqual(s.get("dock.size"), 64)
        self.assertEqual(s.get("dock.position"), "bottom")  # invalid -> default

    def test_atomic_write_leaves_no_temp_files(self):
        s = Settings(self.path)
        for i in range(5):
            s.set("icon_size", 24 + i)
        names = [p.name for p in self.path.parent.iterdir()]
        self.assertEqual(names, ["settings.json"])

    def test_reset(self):
        s = Settings(self.path); s.set("theme", "light"); s.reset()
        self.assertEqual(Settings(self.path).get("theme"), "auto")

    def test_defaults_not_mutated(self):
        s = Settings(self.path); s.set("dock.size", 100)
        self.assertEqual(config.DEFAULTS["dock"]["size"], 56)

    def test_cli_value_parsing(self):
        self.assertIs(config.parse_cli_value("true"), True)
        self.assertEqual(config.parse_cli_value("42"), 42)
        self.assertEqual(config.parse_cli_value("1.5"), 1.5)
        self.assertEqual(config.parse_cli_value("dark"), "dark")


if __name__ == "__main__":
    unittest.main()
