#!/usr/bin/env python3
"""Generate KDE color schemes (.colors) from theme/tokens.json.

Usage: python3 tools/gen_colorschemes.py [output_dir]
Default output: theme/color-schemes/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "theme" / "tokens.json"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    if len(v) != 6:
        raise ValueError(f"bad hex colour: {value!r}")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def rgb_str(value: str) -> str:
    return "{},{},{}".format(*hex_to_rgb(value))


def _lin(c: int) -> float:
    s = c / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    r, g, b = (_lin(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two #RRGGBB colours."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _colors_section(name: str, bg: str, bg_alt: str, fg: str, t: dict) -> list[str]:
    return [
        f"[Colors:{name}]",
        f"BackgroundNormal={rgb_str(bg)}",
        f"BackgroundAlternate={rgb_str(bg_alt)}",
        f"DecorationFocus={rgb_str(t['accent'])}",
        f"DecorationHover={rgb_str(t['accent_hover'])}",
        f"ForegroundNormal={rgb_str(fg)}",
        f"ForegroundActive={rgb_str(t['accent_hover'])}",
        f"ForegroundInactive={rgb_str(t['fg_inactive'])}",
        f"ForegroundLink={rgb_str(t['link'])}",
        f"ForegroundVisited={rgb_str(t['visited'])}",
        f"ForegroundNegative={rgb_str(t['negative'])}",
        f"ForegroundNeutral={rgb_str(t['neutral'])}",
        f"ForegroundPositive={rgb_str(t['positive'])}",
        "",
    ]


def build_scheme(name: str, t: dict) -> str:
    out: list[str] = []
    out += _colors_section("View", t["view_bg"], t["view_bg_alt"], t["fg"], t)
    out += _colors_section("Window", t["bg"], t["bg_alt"], t["fg"], t)
    out += _colors_section("Button", t["button_bg"], t["button_bg_alt"], t["fg"], t)
    out += _colors_section("Tooltip", t["bg"], t["bg_alt"], t["fg"], t)
    out += _colors_section("Complementary", t["header_bg"], t["bg"], t["fg"], t)
    out += _colors_section("Header", t["header_bg"], t["bg"], t["fg"], t)

    sel = _colors_section("Selection", t["selection_bg"], t["selection_bg"], t["selection_fg"], t)
    # Selected text keeps the same colour in every state so it stays readable.
    sel = [
        ln if not ln.startswith(("ForegroundInactive=", "ForegroundActive="))
        else ln.split("=")[0] + "=" + rgb_str(t["selection_fg"])
        for ln in sel
    ]
    out += sel

    out += [
        "[ColorEffects:Disabled]",
        "Color=56,56,56", "ColorAmount=0", "ColorEffect=0",
        "ContrastAmount=0.65", "ContrastEffect=1",
        "IntensityAmount=0.1", "IntensityEffect=2", "",
        "[ColorEffects:Inactive]",
        "ChangeSelectionColor=true", "Color=112,111,110", "ColorAmount=0.025",
        "ColorEffect=2", "ContrastAmount=0.1", "ContrastEffect=2",
        "Enable=false", "IntensityAmount=0", "IntensityEffect=0", "",
        "[General]",
        f"ColorScheme={name}",
        f"Name={name}",
        "shadeSortColumn=true", "",
        "[KDE]",
        "contrast=4", "",
        "[WM]",
        f"activeBackground={rgb_str(t['header_bg'])}",
        f"activeForeground={rgb_str(t['fg'])}",
        f"inactiveBackground={rgb_str(t['bg'])}",
        f"inactiveForeground={rgb_str(t['fg_inactive'])}",
        "",
    ]
    return "\n".join(out)


LNF_ID = "org.novaos.desktop"


def build_kdeglobals(name: str, t: dict) -> str:
    """System-wide default /etc/xdg/kdeglobals: the scheme's colours (that is what KDE
    apps actually read) plus the NovaOS global theme as default."""
    text = build_scheme(name, t)
    marker = "[KDE]\ncontrast=4\n"
    if marker not in text:
        raise RuntimeError("scheme template changed: [KDE] section not found")
    return text.replace(marker, marker + f"LookAndFeelPackage={LNF_ID}\nwidgetStyle=Breeze\n")


def main(argv: list[str]) -> int:
    outdir = Path(argv[1]) if len(argv) > 1 else ROOT / "theme" / "color-schemes"
    outdir.mkdir(parents=True, exist_ok=True)
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    for name, scheme in tokens["schemes"].items():
        path = outdir / f"{name}.colors"
        path.write_text(build_scheme(name, scheme), encoding="utf-8")
        print(f"wrote {path}")
    (outdir / "kdeglobals.dark").write_text(
        build_kdeglobals("NovaDark", tokens["schemes"]["NovaDark"]), encoding="utf-8")
    print(f"wrote {outdir / 'kdeglobals.dark'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
