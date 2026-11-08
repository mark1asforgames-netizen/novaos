import subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from novacore import updates

SIM = """NOTE: This is only a simulation!
Inst libc6 [2.39-0ubuntu8.3] (2.39-0ubuntu8.4 Ubuntu:24.04/noble-updates, Ubuntu:24.04/noble-security [amd64])
Inst openssl [3.0.13-0ubuntu3.4] (3.0.13-0ubuntu3.5 Ubuntu:24.04/noble-updates [amd64])
Inst brand-new-pkg (1.0 Ubuntu:24.04/noble [amd64])
Conf libc6 (2.39-0ubuntu8.4 Ubuntu:24.04/noble-updates [amd64])
Remv oldpkg [1.0]
"""


def fake_runner(stdout="", stderr="", code=0, exc=None):
    def run(cmd, **kw):
        if exc:
            raise exc
        return subprocess.CompletedProcess(cmd, code, stdout, stderr)
    return run


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse(self):
        p = updates.parse_simulation(SIM)
        self.assertEqual([x.name for x in p], ["libc6", "openssl", "brand-new-pkg"])
        self.assertEqual(p[0].old, "2.39-0ubuntu8.3")
        self.assertEqual(p[0].new, "2.39-0ubuntu8.4")
        self.assertTrue(p[0].security)       # multi-repo line containing -security
        self.assertFalse(p[1].security)
        self.assertIsNone(p[2].old)          # newly installed dependency
        self.assertNotIn("noble [amd64]", p[2].repo)  # arch tag stripped

    def test_parse_empty(self):
        self.assertEqual(updates.parse_simulation("Reading...\n0 upgraded\n"), [])

    def test_check_ok_records_time(self):
        st = updates.check(fake_runner(SIM), root=Path(self.tmp.name), state=self.state)
        self.assertTrue(st.ok); self.assertEqual(len(st.pending), 3); self.assertEqual(st.security_count, 1)
        self.assertIsNotNone(updates.last_checked(self.state))

    def test_check_failure_reports_error_and_does_not_record(self):
        st = updates.check(fake_runner(stderr="E: boom\nE: could not lock", code=100), state=self.state)
        self.assertFalse(st.ok); self.assertEqual(st.error, "E: could not lock")
        self.assertIsNone(updates.last_checked(self.state))

    def test_missing_apt(self):
        st = updates.check(fake_runner(exc=FileNotFoundError()), state=self.state)
        self.assertFalse(st.ok); self.assertIn("apt-get not found", st.error)

    def test_timeout(self):
        st = updates.check(fake_runner(exc=subprocess.TimeoutExpired("apt-get", 1)), state=self.state)
        self.assertFalse(st.ok); self.assertIn("timed out", st.error)

    def test_index_age(self):
        root = Path(self.tmp.name)
        stamp = root / "var/lib/apt/periodic/update-success-stamp"
        stamp.parent.mkdir(parents=True); stamp.write_text("")
        import os; os.utime(stamp, (1000, 1000))
        self.assertEqual(updates.index_age(root, now=1600), 600)
        self.assertIsNone(updates.index_age(Path(self.tmp.name) / "nothing"))

    def test_install_requires_privilege_wrapper(self):
        self.assertEqual(updates.install_command()[0], "pkexec")
        self.assertEqual(updates.refresh_command()[0], "pkexec")


if __name__ == "__main__":
    unittest.main()
