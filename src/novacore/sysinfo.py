"""Read real system information from /etc, /proc and /sys.

Every function takes an optional root path so it can be tested against fixtures.
Nothing here is simulated: if data is missing, None is returned.
"""
from __future__ import annotations

import os
import shutil
import socket
from dataclasses import dataclass, asdict
from pathlib import Path


def parse_os_release(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key.strip()] = val
    return out


def parse_cpu_model(cpuinfo: str) -> str | None:
    for line in cpuinfo.splitlines():
        if line.lower().startswith(("model name", "hardware", "cpu model")):
            _, _, val = line.partition(":")
            return " ".join(val.split()) or None
    return None


def count_cpus(cpuinfo: str) -> int:
    return sum(1 for ln in cpuinfo.splitlines() if ln.startswith("processor"))


def parse_meminfo(text: str) -> dict[str, int]:
    """Return values in bytes."""
    out: dict[str, int] = {}
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        parts = rest.split()
        if parts and parts[0].isdigit():
            mult = 1024 if len(parts) > 1 and parts[1].lower() == "kb" else 1
            out[key.strip()] = int(parts[0]) * mult
    return out


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def battery(root: Path = Path("/")) -> dict | None:
    base = root / "sys/class/power_supply"
    try:
        entries = sorted(base.iterdir())
    except OSError:
        return None
    for e in entries:
        if (_read(e / "type") or "").strip() == "Battery":
            cap = (_read(e / "capacity") or "").strip()
            return {
                "percent": int(cap) if cap.isdigit() else None,
                "status": (_read(e / "status") or "Unknown").strip(),
            }
    return None


@dataclass
class SystemInfo:
    os_name: str
    os_version: str
    novaos_version: str | None
    hostname: str
    kernel: str
    cpu_model: str | None
    cpu_count: int
    ram_total: int | None
    ram_available: int | None
    disk_total: int
    disk_free: int
    uptime_seconds: float | None
    battery: dict | None

    def as_dict(self) -> dict:
        return asdict(self)


def collect(root: Path = Path("/"), disk_path: str | None = None) -> SystemInfo:
    osr = parse_os_release(_read(root / "etc/os-release") or "")
    cpuinfo = _read(root / "proc/cpuinfo") or ""
    mem = parse_meminfo(_read(root / "proc/meminfo") or "")
    up = (_read(root / "proc/uptime") or "").split()
    du = shutil.disk_usage(disk_path or str(root))
    nova = _read(root / "etc/novaos-release")
    return SystemInfo(
        os_name=osr.get("NAME", "Unknown"),
        os_version=osr.get("VERSION", osr.get("VERSION_ID", "")),
        novaos_version=nova.strip() if nova else None,
        hostname=socket.gethostname() if root == Path("/") else (_read(root / "etc/hostname") or "").strip(),
        kernel=os.uname().release if root == Path("/") else (_read(root / "proc/sys/kernel/osrelease") or "").strip(),
        cpu_model=parse_cpu_model(cpuinfo),
        cpu_count=count_cpus(cpuinfo),
        ram_total=mem.get("MemTotal"),
        ram_available=mem.get("MemAvailable"),
        disk_total=du.total,
        disk_free=du.free,
        uptime_seconds=float(up[0]) if up else None,
        battery=battery(root),
    )


def human_bytes(n: int | None) -> str:
    if n is None:
        return "n/a"
    f = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if f < 1024 or unit == "TiB":
            return f"{f:.0f} {unit}" if unit == "B" else f"{f:.1f} {unit}"
        f /= 1024
    return f"{f:.1f} TiB"
