#!/usr/bin/env bash
# One-line setup: `ollama pull` for every model named in config/model_registry.yaml.
set -euo pipefail

MODELS=(
    "qwen2.5:0.5b"
    "qwen3.5"
    "gemma2:27b"
    "nomic-embed-text"
)

for model in "${MODELS[@]}"; do
    echo "Pulling ${model}..."
    ollama pull "${model}"
done
