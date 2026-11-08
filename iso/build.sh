#!/usr/bin/env bash
# Build the NovaOS ISO with Debian live-build.
# Must run as root on Debian 13 (or in a debian:trixie container: see .github/workflows).
#   OUT  = where finished ISO + build.log go   (default: ./out)
#   WORK = scratch directory, needs ~10 GB     (default: /tmp/novaos-build)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${OUT:-$SRC/out}"
WORK="${WORK:-/tmp/novaos-build}"
VERSION="$(tr -d '[:space:]' < "$SRC/VERSION")"

[ "$(id -u)" = 0 ] || { echo "ERROR: run as root" >&2; exit 1; }
if ! command -v lb >/dev/null; then
    apt-get update
    apt-get install -y live-build
fi

rm -rf "$WORK"
mkdir -p "$WORK" "$OUT"
cp -a "$SRC/iso/config" "$WORK/config"

# One source of truth for the theme: copy generated files from theme/.
inc="$WORK/config/includes.chroot"
install -d "$inc/usr/share/color-schemes" "$inc/etc/xdg"
install -m 0644 "$SRC"/theme/color-schemes/*.colors "$inc/usr/share/color-schemes/"
install -m 0644 "$SRC/theme/color-schemes/kdeglobals.dark" "$inc/etc/xdg/kdeglobals"
echo "NovaOS $VERSION" > "$inc/etc/novaos-release"

# Archives/uploads can drop the executable bit; hooks must be runnable.
find "$WORK/config/hooks" -type f -exec chmod 0755 {} +

cd "$WORK"
lb config \
    --distribution trixie \
    --architectures amd64 \
    --archive-areas "main contrib non-free-firmware" \
    --binary-images iso-hybrid \
    --debian-installer none \
    --memtest none \
    --apt-indices false \
    --chroot-squashfs-compression-type xz \
    --iso-application "NovaOS" \
    --iso-publisher "NovaOS project" \
    --iso-volume "NOVAOS" \
    --image-name "novaos-$VERSION" \
    --bootappend-live "boot=live components quiet splash hostname=novaos username=nova locales=en_US.UTF-8"

set +e
lb build 2>&1 | tee "$OUT/build.log"
rc=${PIPESTATUS[0]}
set -e
[ "$rc" = 0 ] || { echo "ERROR: lb build failed (exit $rc). See $OUT/build.log" >&2; exit "$rc"; }

iso="$(ls -1 "$WORK"/*.iso 2>/dev/null | head -n1 || true)"
[ -n "$iso" ] || { echo "ERROR: build finished but no .iso found" >&2; exit 1; }
cp "$iso" "$OUT/novaos-$VERSION-amd64.iso"
( cd "$OUT" && sha256sum "novaos-$VERSION-amd64.iso" > SHA256SUMS )
echo "OK: $OUT/novaos-$VERSION-amd64.iso"
cat "$OUT/SHA256SUMS"
