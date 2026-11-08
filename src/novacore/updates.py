"""Real update status via apt.

* check() simulates an upgrade (`apt-get -s`), which needs NO root and changes nothing.
  It reflects the *local package index*, so it also reports how old that index is.
* Refreshing the index and installing need root. This module only builds the commands
  (refresh_command / install_command); the UI must show the list and get explicit user
  confirmation before running them via pkexec (spec §6.10, §11).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

_INST = re.compile(r"^Inst (\S+)(?: \[([^\]]+)\])? \((\S+) (.*)\)\s*$")
_ARCH = re.compile(r"\s*\[[^\]]*\]\s*$")

SIM_CMD = ["apt-get", "-s", "-o", "Debug::NoLocking=1", "dist-upgrade"]
STAMP_PATHS = (
    "var/lib/apt/periodic/update-success-stamp",
    "var/lib/apt/lists",
)


@dataclass(frozen=True)
class PendingUpdate:
    name: str
    old: str | None
    new: str
    repo: str
    security: bool


@dataclass
class UpdateStatus:
    ok: bool
    error: str | None = None
    pending: list[PendingUpdate] = field(default_factory=list)
    index_age_seconds: float | None = None
    checked_at: float | None = None

    @property
    def security_count(self) -> int:
        return sum(1 for p in self.pending if p.security)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["security_count"] = self.security_count
        return d


def parse_simulation(text: str) -> list[PendingUpdate]:
    out: list[PendingUpdate] = []
    for line in text.splitlines():
        m = _INST.match(line)
        if not m:
            continue
        name, old, new, repo = m.groups()
        repo = _ARCH.sub("", repo)
        out.append(PendingUpdate(name, old, new, repo, "-security" in repo))
    return out


def index_age(root: Path = Path("/"), now: float | None = None) -> float | None:
    now = time.time() if now is None else now
    for rel in STAMP_PATHS:
        p = root / rel
        try:
            return max(0.0, now - p.stat().st_mtime)
        except OSError:
            continue
    return None


def state_path() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state")
    return Path(base) / "novaos" / "updates.json"


def last_checked(path: Path | None = None) -> float | None:
    try:
        return float(json.loads((path or state_path()).read_text())["checked_at"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _remember(ts: float, path: Path | None = None) -> None:
    p = path or state_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"checked_at": ts}))
    except OSError:
        pass  # non-fatal: only used for display


def check(runner=subprocess.run, root: Path = Path("/"), state: Path | None = None) -> UpdateStatus:
    now = time.time()
    try:
        proc = runner(SIM_CMD, capture_output=True, text=True, timeout=120,
                      env={**os.environ, "LC_ALL": "C"})
    except FileNotFoundError:
        return UpdateStatus(False, "apt-get not found (not a Debian/Ubuntu system?)")
    except subprocess.TimeoutExpired:
        return UpdateStatus(False, "update check timed out")
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "apt-get failed").strip().splitlines()
        return UpdateStatus(False, msg[-1] if msg else "apt-get failed")
    _remember(now, state)
    return UpdateStatus(True, None, parse_simulation(proc.stdout), index_age(root, now), now)


def refresh_command() -> list[str]:
    """Refresh package lists (needs admin auth via polkit)."""
    return ["pkexec", "apt-get", "update"]


def install_command() -> list[str]:
    """Install pending updates. Callers MUST obtain explicit user confirmation first."""
    return ["pkexec", "apt-get", "dist-upgrade", "-y"]
