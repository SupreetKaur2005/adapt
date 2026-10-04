#!/usr/bin/env bash
# Tears down and rebuilds the Docker/Mininet environment from scratch.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "[INFO] Resetting A.D.A.P.T. sandbox environment..."

# 1. Clean up Mininet virtual network interfaces and namespaces if mn is installed
if command -v mn >/dev/null 2>&1; then
    echo "[INFO] Cleaning up Mininet network topology..."
    if [ "$(id -u)" -eq 0 ]; then
        mn -c >/dev/null 2>&1 || true
    elif command -v sudo >/dev/null 2>&1; then
        sudo mn -c >/dev/null 2>&1 || true
    else
        mn -c >/dev/null 2>&1 || true
    fi
else
    echo "[INFO] Mininet (mn) not found in PATH; skipping Mininet cleanup."
fi

# 2. Check Docker availability and reset containers
if ! command -v docker >/dev/null 2>&1; then
    echo "[WARN] Docker CLI not found in PATH; skipping container reset."
    exit 0
fi

if ! docker info >/dev/null 2>&1; then
    echo "[WARN] Docker daemon is not running or accessible; skipping container reset."
    exit 0
fi

COMPOSE_FILE="docker/docker-compose.yml"
if [ ! -f "${COMPOSE_FILE}" ]; then
    echo "[ERROR] Docker compose file not found at ${COMPOSE_FILE}" >&2
    exit 1
fi

echo "[INFO] Tearing down existing sandbox containers and volumes..."
docker compose -f "${COMPOSE_FILE}" down -v || echo "[INFO] No existing containers to tear down."

echo "[INFO] Rebuilding and launching sandbox containers..."
docker compose -f "${COMPOSE_FILE}" up -d --build

echo "[INFO] A.D.A.P.T. sandbox environment reset complete."
