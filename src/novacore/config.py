"""NovaOS user settings store (~/.config/novaos/settings.json).

Rules (spec §11/§13): settings persist across reboots, writes are atomic, unknown or
invalid values are rejected, and no secrets are ever stored here.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

DEFAULTS: dict = {
    "theme": "auto",               # light | dark | auto
    "accent": "violet",            # violet | blue
    "transparency": 70,            # 0..100
    "animations": True,
    "icon_size": 48,               # 24..128
    "font_scale": 1.0,             # 0.8..2.0
    "dock": {"position": "bottom", "size": 56, "autohide": False},
    "desktop_icons": True,
    "focus_mode": False,
}

_ENUMS = {
    "theme": {"light", "dark", "auto"},
    "accent": {"violet", "blue"},
    "dock.position": {"bottom", "left", "right"},
}
_RANGES = {
    "transparency": (0, 100),
    "icon_size": (24, 128),
    "font_scale": (0.8, 2.0),
    "dock.size": (32, 128),
}


class SettingsError(ValueError):
    pass


def default_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "novaos" / "settings.json"


def _walk(d: dict, prefix: str = ""):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from _walk(v, f"{prefix}{k}.")
        else:
            yield f"{prefix}{k}", v


def validate(key: str, value):
    flat = dict(_walk(DEFAULTS))
    if key not in flat:
        raise SettingsError(f"unknown setting: {key}")
    expected = type(flat[key])
    if expected is bool:
        if not isinstance(value, bool):
            raise SettingsError(f"{key} must be true/false")
    elif expected is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SettingsError(f"{key} must be an integer")
    elif expected is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SettingsError(f"{key} must be a number")
        value = float(value)
    elif expected is str and not isinstance(value, str):
        raise SettingsError(f"{key} must be a string")
    if key in _ENUMS and value not in _ENUMS[key]:
        raise SettingsError(f"{key} must be one of {sorted(_ENUMS[key])}")
    if key in _RANGES:
        lo, hi = _RANGES[key]
        if not lo <= value <= hi:
            raise SettingsError(f"{key} must be between {lo} and {hi}")
    return value


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()
        self.data = copy.deepcopy(DEFAULTS)
        self.load_error: str | None = None
        self.load()

    def load(self) -> None:
        """Load from disk. A missing file means defaults; a corrupt file is
        kept aside as *.corrupt and defaults are used (never crash the desktop)."""
        self.data = copy.deepcopy(DEFAULTS)
        self.load_error = None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError) as exc:
            self.load_error = f"could not read settings: {exc}"
            try:
                self.path.replace(self.path.with_suffix(".json.corrupt"))
            except OSError:
                pass
            return
        if not isinstance(raw, dict):
            self.load_error = "settings file is not an object"
            return
        for key, value in _walk(raw):
            try:
                self._set_raw(key, validate(key, value))
            except SettingsError:
                continue  # ignore bad/unknown entries, keep default

    def _set_raw(self, key: str, value) -> None:
        node = self.data
        parts = key.split(".")
        for p in parts[:-1]:
            node = node[p]
        node[parts[-1]] = value

    def get(self, key: str):
        node = self.data
        try:
            for p in key.split("."):
                node = node[p]
        except (KeyError, TypeError):
            raise SettingsError(f"unknown setting: {key}") from None
        if isinstance(node, dict):
            raise SettingsError(f"{key} is a group, not a setting")
        return node

    def set(self, key: str, value) -> None:
        self._set_raw(key, validate(key, value))
        self.save()

    def reset(self) -> None:
        self.data = copy.deepcopy(DEFAULTS)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".settings-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, sort_keys=True)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise


def parse_cli_value(text: str):
    low = text.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text
