import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from novacore import sysinfo

OSR = '''NAME="Ubuntu"
VERSION="24.04.1 LTS (Noble Numbat)"
# comment
ID=ubuntu
VERSION_ID="24.04"
'''
CPU = "processor\t: 0\nmodel name\t: Intel(R) Core(TM)  i7-1165G7\nprocessor\t: 1\nmodel name\t: Intel(R) Core(TM)  i7-1165G7\n"
MEM = "MemTotal:       16384000 kB\nMemFree:  100 kB\nMemAvailable:    8192000 kB\nHugePages_Total:       0\n"


class Parsing(unittest.TestCase):
    def test_os_release(self):
        d = sysinfo.parse_os_release(OSR)
        self.assertEqual(d["NAME"], "Ubuntu")
        self.assertEqual(d["VERSION_ID"], "24.04")
        self.assertNotIn("# comment", d)

    def test_cpu(self):
        self.assertEqual(sysinfo.parse_cpu_model(CPU), "Intel(R) Core(TM) i7-1165G7")
        self.assertEqual(sysinfo.count_cpus(CPU), 2)
        self.assertIsNone(sysinfo.parse_cpu_model(""))

    def test_meminfo_bytes(self):
        m = sysinfo.parse_meminfo(MEM)
        self.assertEqual(m["MemTotal"], 16384000 * 1024)
        self.assertEqual(m["HugePages_Total"], 0)

    def test_human_bytes(self):
        self.assertEqual(sysinfo.human_bytes(None), "n/a")
        self.assertEqual(sysinfo.human_bytes(512), "512 B")
        self.assertEqual(sysinfo.human_bytes(1536), "1.5 KiB")
        self.assertEqual(sysinfo.human_bytes(16 * 1024**3), "16.0 GiB")


class FakeRoot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel, txt in {
            "etc/os-release": OSR, "etc/hostname": "nova-pc\n",
            "etc/novaos-release": "NovaOS 0.1.0\n",
            "proc/cpuinfo": CPU, "proc/meminfo": MEM, "proc/uptime": "3600.55 100.0\n",
            "proc/sys/kernel/osrelease": "6.8.0-test\n",
        }.items():
            p = self.root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt)

    def tearDown(self):
        self.tmp.cleanup()

    def test_collect_fixture(self):
        i = sysinfo.collect(self.root)
        self.assertEqual(i.hostname, "nova-pc")
        self.assertEqual(i.novaos_version, "NovaOS 0.1.0")
        self.assertEqual(i.cpu_count, 2)
        self.assertEqual(i.ram_total, 16384000 * 1024)
        self.assertEqual(i.uptime_seconds, 3600.55)
        self.assertIsNone(i.battery)  # desktop: no battery, must not invent one

    def test_battery_detected(self):
        b = self.root / "sys/class/power_supply/BAT0"; b.mkdir(parents=True)
        (b / "type").write_text("Battery\n"); (b / "capacity").write_text("73\n"); (b / "status").write_text("Discharging\n")
        ac = self.root / "sys/class/power_supply/AC"; ac.mkdir(parents=True); (ac / "type").write_text("Mains\n")
        self.assertEqual(sysinfo.battery(self.root), {"percent": 73, "status": "Discharging"})

    def test_missing_files_do_not_crash(self):
        empty = tempfile.TemporaryDirectory()
        i = sysinfo.collect(Path(empty.name))
        self.assertIsNone(i.cpu_model); self.assertIsNone(i.ram_total)
        empty.cleanup()


class LiveHost(unittest.TestCase):
    """Runs against the real machine executing the tests."""
    def test_live(self):
        i = sysinfo.collect()
        self.assertTrue(i.hostname)
        self.assertGreater(i.ram_total, 0)
        self.assertGreater(i.disk_total, 0)
        self.assertGreaterEqual(i.cpu_count, 1)


if __name__ == "__main__":
    unittest.main()
