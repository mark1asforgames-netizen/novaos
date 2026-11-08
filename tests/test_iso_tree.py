"""Static checks of the ISO build tree. They catch typos and missing files; they do NOT
prove that live-build or Plasma accept the configuration (that needs a real build)."""
import json, os, re, shutil, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "iso" / "config"
INC = CFG / "includes.chroot"
LAYOUT = INC / "usr/share/plasma/look-and-feel/org.novaos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js"


class TreeTests(unittest.TestCase):
    def test_json_metadata_valid(self):
        for rel in ("usr/share/plasma/look-and-feel/org.novaos.desktop/metadata.json",
                    "usr/share/wallpapers/NovaOS/metadata.json"):
            d = json.loads((INC / rel).read_text())
            self.assertIn("KPlugin", d); self.assertIn("KPackageStructure", d)
        lnf = json.loads((INC / "usr/share/plasma/look-and-feel/org.novaos.desktop/metadata.json").read_text())
        self.assertEqual(lnf["KPlugin"]["Id"], "org.novaos.desktop")
        self.assertEqual(lnf["KPackageStructure"], "Plasma/LookAndFeel")

    def test_lnf_defaults_reference_existing_scheme(self):
        text = (INC / "usr/share/plasma/look-and-feel/org.novaos.desktop/contents/defaults").read_text()
        m = re.search(r"ColorScheme=(\w+)", text)
        self.assertTrue(m)
        self.assertTrue((ROOT / "theme/color-schemes" / f"{m.group(1)}.colors").exists())

    def test_wallpaper_is_real_image(self):
        img = INC / "usr/share/wallpapers/NovaOS/contents/images/3840x2160.jpg"
        data = img.read_bytes()
        self.assertEqual(data[:3], b"\xff\xd8\xff")      # JPEG magic
        self.assertGreater(len(data), 100_000)

    def test_desktop_links(self):
        for n in ("home", "trash"):
            t = (INC / f"etc/skel/Desktop/{n}.desktop").read_text()
            self.assertIn("[Desktop Entry]", t); self.assertIn("Type=Link", t); self.assertRegex(t, r"URL(\[\$e\])?=")

    def test_package_list_clean(self):
        names = [l.strip() for l in (CFG / "package-lists/novaos.list.chroot").read_text().splitlines()
                 if l.strip() and not l.startswith("#")]
        self.assertEqual(len(names), len(set(names)), "duplicate packages")
        for n in names:
            self.assertRegex(n, r"^[a-z0-9][a-z0-9+.\-]+$", n)
        for must in ("plasma-desktop", "sddm", "calamares", "dolphin", "konsole", "plasma-nm", "plasma-pa"):
            self.assertIn(must, names)

    def test_scripts_syntax(self):
        for f in [ROOT / "iso/build.sh", *sorted((CFG / "hooks/live").iterdir())]:
            sh = "bash" if f.suffix == ".sh" else "sh"
            r = subprocess.run([sh, "-n", str(f)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{f.name}: {r.stderr}")

    def test_build_script_is_safe(self):
        s = (ROOT / "iso/build.sh").read_text()
        self.assertIn("set -euo pipefail", s)
        self.assertIn('id -u', s)           # refuses to run unprivileged
        self.assertIn("--debian-installer none", s)
        self.assertIn("SHA256SUMS", s)

    def test_verify_hook_fails_the_build_on_missing_files(self):
        h = (CFG / "hooks/live/9000-verify.hook.chroot").read_text()
        for needle in ("org.novaos.desktop", "NovaDark.colors", "kdeglobals", "calamares", "exit $bad"):
            self.assertIn(needle, h)

    def test_every_verified_path_is_provided_by_repo_or_build(self):
        """Files the verify hook demands must be shipped by includes.chroot or copied by build.sh."""
        h = (CFG / "hooks/live/9000-verify.hook.chroot").read_text()
        paths = re.findall(r"^\s+(/[\w./\-]+?)\s*\\?$", h, re.M)
        self.assertGreater(len(paths), 8)
        generated = {"/usr/share/color-schemes/NovaDark.colors", "/usr/share/color-schemes/NovaLight.colors",
                     "/etc/xdg/kdeglobals", "/etc/novaos-release"}   # created by build.sh
        for p in paths:
            if p in generated:
                continue
            self.assertTrue((INC / p.lstrip("/")).exists(), f"verify hook expects {p} but repo does not ship it")

    def test_workflow(self):
        w = (ROOT / ".github/workflows/build-iso.yml").read_text()
        for needle in ("workflow_dispatch", "debian:trixie", "--privileged", "gh release create", "unittest"):
            self.assertIn(needle, w)
        try:
            import yaml
            yaml.safe_load(w)
        except ImportError:
            pass


@unittest.skipUnless(shutil.which("node"), "node not installed")
class LayoutScript(unittest.TestCase):
    def run_layout(self, *extra):
        r = subprocess.run(["node", str(ROOT / "tests/layout_mock.js"), str(LAYOUT), *extra],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def check_common(self, out):
        self.assertEqual(len(out["panels"]), 2)
        top, dock = out["panels"]
        self.assertEqual(top["location"], "top")
        types = [w["type"] for w in top["widgets"]]
        self.assertEqual(types[0], "org.kde.plasma.kickoff")                 # launcher first
        self.assertIn("org.kde.plasma.digitalclock", types)
        self.assertEqual(types[-1], "org.kde.plasma.systemtray")             # tray on the right
        self.assertLess(types.index("org.kde.plasma.panelspacer"), types.index("org.kde.plasma.digitalclock"))
        self.assertEqual(dock["location"], "bottom")
        self.assertEqual(dock["alignment"], "center")
        tasks = [w for w in dock["widgets"] if w["type"] == "org.kde.plasma.icontasks"]
        self.assertEqual(len(tasks), 1)
        launchers = tasks[0]["config"]["launchers"]
        for app in ("dolphin", "konsole", "systemsettings", "firefox-esr"):
            self.assertIn(app, launchers)
        d = out["desktops"][0]
        self.assertEqual(d["plugin"], "org.kde.image")
        self.assertEqual(d["config"]["Image"], "file:///usr/share/wallpapers/NovaOS")

    def test_full_api(self):
        out = self.run_layout()
        self.check_common(out)
        self.assertTrue(out["panels"][1]["floating"])
        self.assertTrue(any(w["type"] == "org.kde.plasma.trash" for w in out["panels"][1]["widgets"]))

    def test_degraded_api_does_not_abort(self):
        """Old Plasma without floating/lengthMode/trash must still yield the full layout."""
        self.check_common(self.run_layout("degraded"))

    def test_node_syntax(self):
        r = subprocess.run(["node", "--check", str(LAYOUT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
