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
  "$BUILD_DIR/usr/share/applications"

install -m 0644 gui.py "$BUILD_DIR/opt/autoshutdown/gui.py"
install -m 0644 autoshutdown.py "$BUILD_DIR/opt/autoshutdown/autoshutdown.py"

cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: autoshutdown
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.10), python3-tk, python3-psutil
Maintainer: Hubuntu OS Project
Description: Compact timed shutdown and application-control utility
 AutoShutdown provides timed shutdown, restart, logout, close-app and
 temporary restrict-app features through a compact desktop interface.
EOF

cat > "$BUILD_DIR/usr/bin/autoshutdown" <<'EOF'
#!/usr/bin/env bash
exec python3 /opt/autoshutdown/gui.py "$@"
EOF
chmod 0755 "$BUILD_DIR/usr/bin/autoshutdown"

cat > "$BUILD_DIR/usr/share/applications/autoshutdown.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=AutoShutdown
Comment=Timed shutdown and application control
Exec=autoshutdown
Terminal=false
Categories=Utility;System;
StartupNotify=true
EOF

mkdir -p "$ROOT_DIR/dist"
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$ROOT_DIR/dist/${PKG}.deb"

echo "Built: dist/${PKG}.deb"
