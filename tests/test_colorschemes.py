import configparser, json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gen_colorschemes as g

TOKENS = json.loads((ROOT / "theme" / "tokens.json").read_text())
REQUIRED = {"BackgroundNormal", "BackgroundAlternate", "DecorationFocus", "DecorationHover",
            "ForegroundNormal", "ForegroundActive", "ForegroundInactive", "ForegroundLink",
            "ForegroundVisited", "ForegroundNegative", "ForegroundNeutral", "ForegroundPositive"}
SECTIONS = ["View", "Window", "Button", "Selection", "Tooltip", "Complementary", "Header"]


def parse(text):
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str  # KDE keys are case sensitive
    cp.read_string(text)
    return cp


class SchemeTests(unittest.TestCase):
    def test_color_math(self):
        self.assertAlmostEqual(g.contrast("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(g.contrast("#777777", "#777777"), 1.0, places=3)
        self.assertEqual(g.rgb_str("#0B1026"), "11,16,38")
        with self.assertRaises(ValueError):
            g.hex_to_rgb("#12345")

    def test_each_scheme_structure(self):
        for name, t in TOKENS["schemes"].items():
            cp = parse(g.build_scheme(name, t))
            self.assertEqual(cp["General"]["Name"], name)
            for s in SECTIONS:
                sec = cp[f"Colors:{s}"]
                self.assertTrue(REQUIRED <= set(sec), f"{name}/{s} missing keys")
                for k in REQUIRED:
                    rgb = [int(x) for x in sec[k].split(",")]
                    self.assertEqual(len(rgb), 3); self.assertTrue(all(0 <= x <= 255 for x in rgb))

    def test_all_tokens_present_in_both_schemes(self):
        keys = [set(s) for s in TOKENS["schemes"].values()]
        self.assertEqual(keys[0], keys[1])

    def test_readability_wcag_aa(self):
        for name, t in TOKENS["schemes"].items():
            for bg in ("bg", "bg_alt", "view_bg", "view_bg_alt", "button_bg", "button_bg_alt", "header_bg"):
                for fg in ("fg", "fg_inactive", "link", "visited", "negative", "neutral", "positive", "accent_hover"):
                    self.assertGreaterEqual(g.contrast(t[bg], t[fg]), 4.5, f"{name}: {fg} on {bg}")
            self.assertGreaterEqual(g.contrast(t["selection_bg"], t["selection_fg"]), 4.5)

    def test_selection_text_never_changes_colour(self):
        for name, t in TOKENS["schemes"].items():
            sel = parse(g.build_scheme(name, t))["Colors:Selection"]
            want = g.rgb_str(t["selection_fg"])
            for k in ("ForegroundNormal", "ForegroundActive", "ForegroundInactive"):
                self.assertEqual(sel[k], want)

    def test_cli_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(g.main(["x", d]), 0)
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ["NovaDark.colors", "NovaLight.colors", "kdeglobals.dark"])

    def test_committed_files_match_generator(self):
        """Committed theme/color-schemes must be regenerated when tokens change."""
        for name, t in TOKENS["schemes"].items():
            f = ROOT / "theme" / "color-schemes" / f"{name}.colors"
            self.assertTrue(f.exists(), f"{f} missing - run `make gen`")
            self.assertEqual(f.read_text(), g.build_scheme(name, t), f"{name} is stale - run `make gen`")

    def test_kdeglobals_default(self):
        cp = parse(g.build_kdeglobals("NovaDark", TOKENS["schemes"]["NovaDark"]))
        self.assertEqual(cp["KDE"]["LookAndFeelPackage"], "org.novaos.desktop")
        self.assertEqual(cp["KDE"]["contrast"], "4")
        self.assertIn("BackgroundNormal", cp["Colors:Window"])  # real colours, not just a name
        f = ROOT / "theme" / "color-schemes" / "kdeglobals.dark"
        self.assertEqual(f.read_text(), g.build_kdeglobals("NovaDark", TOKENS["schemes"]["NovaDark"]))

    def test_brand_palette_present(self):
        for k in ("navy", "graphite", "violet", "blue", "white"):
            self.assertIn(k, TOKENS["palette"])


if __name__ == "__main__":
    unittest.main()
