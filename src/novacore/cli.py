"""novactl – command line front end for novacore."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta

from . import __version__, config, sysinfo, updates


def _cmd_about(args) -> int:
    info = sysinfo.collect()
    if args.json:
        print(json.dumps(info.as_dict(), indent=2))
        return 0
    up = str(timedelta(seconds=int(info.uptime_seconds))) if info.uptime_seconds is not None else "n/a"
    rows = [
        ("NovaOS", info.novaos_version or "not installed (running on a plain Linux host)"),
        ("Base system", f"{info.os_name} {info.os_version}".strip()),
        ("Kernel", info.kernel),
        ("Device name", info.hostname),
        ("Processor", f"{info.cpu_model or 'unknown'} ({info.cpu_count} threads)"),
        ("Memory", f"{sysinfo.human_bytes(info.ram_total)} total, {sysinfo.human_bytes(info.ram_available)} available"),
        ("Disk (/)", f"{sysinfo.human_bytes(info.disk_total)} total, {sysinfo.human_bytes(info.disk_free)} free"),
        ("Uptime", up),
        ("Battery", f"{info.battery['percent']}% ({info.battery['status']})" if info.battery else "none detected"),
    ]
    for k, v in rows:
        print(f"{k:<12} {v}")
    return 0


def _cmd_updates(args) -> int:
    st = updates.check()
    if args.json:
        print(json.dumps(st.as_dict(), indent=2))
        return 0 if st.ok else 1
    if not st.ok:
        print(f"Update check failed: {st.error}", file=sys.stderr)
        return 1
    age = st.index_age_seconds
    print(f"Package index age: {'unknown' if age is None else str(timedelta(seconds=int(age)))}"
          " (run `pkexec apt-get update` to refresh)")
    print(f"{len(st.pending)} update(s) pending, {st.security_count} security")
    for p in st.pending:
        flag = " [security]" if p.security else ""
        print(f"  {p.name}: {p.old or 'new'} -> {p.new}{flag}")
    return 0


def _cmd_config(args) -> int:
    s = config.Settings()
    try:
        if args.action == "get":
            if args.key:
                print(json.dumps(s.get(args.key)))
            else:
                print(json.dumps(s.data, indent=2, sort_keys=True))
        elif args.action == "set":
            if args.key is None or args.value is None:
                print("usage: novactl config set KEY VALUE", file=sys.stderr)
                return 2
            s.set(args.key, config.parse_cli_value(args.value))
        elif args.action == "reset":
            s.reset()
    except config.SettingsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if s.load_error:
        print(f"warning: {s.load_error}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="novactl", description="NovaOS system tool")
    ap.add_argument("--version", action="version", version=f"novacore {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("about", help="show real system information")
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=_cmd_about)
    u = sub.add_parser("updates", help="check pending updates (no root, changes nothing)")
    u.add_argument("--json", action="store_true")
    u.set_defaults(fn=_cmd_updates)
    c = sub.add_parser("config", help="read/write NovaOS settings")
    c.add_argument("action", choices=["get", "set", "reset"])
    c.add_argument("key", nargs="?")
    c.add_argument("value", nargs="?")
    c.set_defaults(fn=_cmd_config)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
