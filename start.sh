#!/usr/bin/env bash
set -euo pipefail

# Resolve project root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_DIR="$ROOT_DIR/release"

# Move to release directory
cd "$RELEASE_DIR"

# Configure ASP.NET Core URLs
export ASPNETCORE_URLS="http://localhost:3000;https://localhost:3001"

# Start the application
exec dotnet KvtmAuto.dll
