#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="${1:-0.2.0}"
ARCH="${2:-all}"
PKG="autoshutdown_${VERSION}_${ARCH}"
BUILD_DIR="$ROOT_DIR/dist/deb/$PKG"

rm -rf "$BUILD_DIR"
mkdir -p \
  "$BUILD_DIR/DEBIAN" \
  "$BUILD_DIR/opt/autoshutdown" \
  "$BUILD_DIR/usr/bin" \
  "$BUILD_DIR/usr/share/applications" \
  "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"

install -m 0644 gui.py "$BUILD_DIR/opt/autoshutdown/gui.py"
install -m 0644 autoshutdown.py "$BUILD_DIR/opt/autoshutdown/autoshutdown.py"
install -m 0644 assets/autoshutdown.svg "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/autoshutdown.svg"

cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: autoshutdown
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.10), python3-tk, python3-psutil, python3-pil, python3-pystray
Maintainer: Hubuntu OS Project
Homepage: https://github.com/haniffzain/autoshutdown
Description: Compact timed shutdown and application-control utility
 AutoShutdown provides timed shutdown, restart, logout, close-app,
 temporary restrict-app, notifications and system-tray controls through
 a compact desktop interface.
EOF

cat > "$BUILD_DIR/usr/bin/autoshutdown" <<'EOF'
#!/usr/bin/env bash
exec python3 /opt/autoshutdown/gui.py "$@"
EOF
chmod 0755 "$BUILD_DIR/usr/bin/autoshutdown"

cat > "$BUILD_DIR/usr/share/applications/autoshutdown.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=AutoShutdown
GenericName=Shutdown Scheduler
Comment=Schedule shutdown, logout, restart and application-control tasks
Exec=autoshutdown
Icon=autoshutdown
Terminal=false
Categories=Utility;System;
Keywords=shutdown;logout;restart;timer;scheduler;restrict;close app;tray;Hubuntu;
StartupNotify=true
X-GNOME-UsesNotifications=true
X-Hubuntu-Application=true
X-Hubuntu-Version=$VERSION
EOF

mkdir -p "$ROOT_DIR/dist"
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$ROOT_DIR/dist/${PKG}.deb"

echo "Built: dist/${PKG}.deb"
