#!/usr/bin/env bash
# Tears down and rebuilds the Docker/Mininet environment from scratch.
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose -f docker/docker-compose.yml down -v
sudo mn -c || true
docker compose -f docker/docker-compose.yml up -d --build
