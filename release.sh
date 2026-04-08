#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_DIR="$ROOT_DIR/release"

rm -rf "$RELEASE_DIR"

# publish backend (frontend is built automatically via csproj BuildClient target)
dotnet publish "$ROOT_DIR/api/KvtmAuto.csproj" -c Release -o "$RELEASE_DIR"
