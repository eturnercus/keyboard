#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VERSION=$(python3 -c "from touchflow import __version__; print(__version__)")
DIST="dist"
rm -rf "$DIST"
mkdir -p "$DIST"

echo "==> Building sdist..."
python3 -m pip install build -q
python3 -m build --sdist --wheel --outdir "$DIST"

echo "==> Creating release archive..."
tar -czf "$DIST/touchflow-keyboard-${VERSION}-linux.tar.gz" \
    --exclude='.git' \
    --exclude='dist' \
    --exclude='__pycache__' \
    -C "$ROOT" .

echo "==> Release artifacts:"
ls -lh "$DIST/"

echo ""
echo "✓ Release $VERSION ready in $DIST/"
