#!/bin/bash
set -e

# Usage:
#   ./deploy.sh [branch] [port]
# Defaults:
#   branch = main
#   port   = 8001

BRANCH="${1:-main}"
PORT="${2:-8001}"
PROJECT_NAME="format-pdf-qr"

# Ensure APP_PORT is available for docker-compose interpolation
echo "APP_PORT=$PORT" > .env

# Check docker availability
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker no está instalado." >&2
  exit 1
fi

# Check docker compose availability (try both v2 and v1)
if docker compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE="docker compose"
elif docker-compose --version >/dev/null 2>&1; then
  DOCKER_COMPOSE="docker-compose"
else
  echo "ERROR: docker compose no está disponible." >&2
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
$DOCKER_COMPOSE -p "$PROJECT_NAME" up -d --build --remove-orphans

# Show status
$DOCKER_COMPOSE -p "$PROJECT_NAME" ps

echo ""
echo "✅ Despliegue completado. App expuesta en http://<tu-servidor>:$PORT/"