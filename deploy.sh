#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./deploy.sh [branch] [port]
# Defaults:
#   branch = main
#   port   = 8001

BRANCH="${1:-main}"
PORT="${2:-8001}"
PROJECT_NAME="format-pdf-qr"

# Ensure APP_PORT is available for docker-compose interpolation
printf "APP_PORT=%s\n" "$PORT" > .env

# Check docker compose availability
if ! command -v docker &>/dev/null; then
  echo "ERROR: docker no está instalado." >&2
  exit 1
fi

if ! docker compose version &>/dev/null; then
  echo "ERROR: docker compose v2 no está disponible." >&2
  exit 1
fi

# Pull latest code if repository exists
if [ -d .git ]; then
  echo "==> Actualizando código (branch: $BRANCH)"
  git fetch --all
  git reset --hard "origin/$BRANCH"
else
  echo "==> No es un repositorio git, se omite 'git pull'"
fi

# Build and (re)start container
echo "==> Construyendo y levantando contenedor ($PROJECT_NAME) en puerto $PORT"
docker compose -p "$PROJECT_NAME" up -d --build --remove-orphans

# Show status
docker compose -p "$PROJECT_NAME" ps

echo "\n✅ Despliegue completado. App expuesta en http://<tu-servidor>:$PORT/"