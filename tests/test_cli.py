import contextlib, io, json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from novacore import cli


def run(*args, env=None):
    out, err = io.StringIO(), io.StringIO()
    old = dict(os.environ)
    os.environ.update(env or {})
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(args))
    finally:
        os.environ.clear(); os.environ.update(old)
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def test_about_text_and_json(self):
        code, out, _ = run("about")
        self.assertEqual(code, 0); self.assertIn("Processor", out)
        code, out, _ = run("about", "--json")
        self.assertEqual(code, 0); self.assertGreater(json.loads(out)["ram_total"], 0)

    def test_config_roundtrip_via_cli(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"XDG_CONFIG_HOME": d}
            self.assertEqual(run("config", "set", "theme", "dark", env=env)[0], 0)
            code, out, _ = run("config", "get", "theme", env=env)
            self.assertEqual((code, json.loads(out)), (0, "dark"))
            code, _, err = run("config", "set", "theme", "neon", env=env)
            self.assertEqual(code, 2); self.assertIn("one of", err)
            self.assertEqual(run("config", "set", "theme", env=env)[0], 2)
            self.assertEqual(run("config", "reset", env=env)[0], 0)
            self.assertEqual(json.loads(run("config", "get", "theme", env=env)[1]), "auto")

    def test_unknown_setting(self):
        with tempfile.TemporaryDirectory() as d:
            code, _, err = run("config", "get", "ghost", env={"XDG_CONFIG_HOME": d})
            self.assertEqual(code, 2); self.assertIn("unknown", err)


if __name__ == "__main__":
    unittest.main()
