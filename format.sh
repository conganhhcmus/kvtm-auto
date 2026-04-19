#!/bin/bash
set -e

echo "Formatting web (Prettier)..."
cd web && npm run format
cd ..

echo "Formatting api (dotnet format)..."
dotnet format api/KvtmAuto.csproj
