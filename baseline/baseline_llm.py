"""A deliberately simple comparison system: one monolithic heavy model
handling every subtask, no CUV routing, no tiering. Used to measure what
routing actually saves.
"""
from __future__ import annotations

from adapt.routing.model_clients.ollama_client import OllamaClient


def run_baseline_llm(subtask: str, model_client: object = None) -> dict:
    """Execute subtask against the fixed heavy tier model."""
    client = model_client or OllamaClient()
    model = "deepseek-coder:33b"
    prompt = f"Analyze the following cyber subtask and propose execution steps:\n{subtask}"

    if hasattr(client, "generate"):
        response = client.generate(model, prompt)
    else:
        response = "Baseline heavy model execution plan."

    cost_per_token = 0.0004
    estimated_tokens = len(prompt.split()) * 4
    total_cost = estimated_tokens * cost_per_token

    return {
        "model": model,
        "subtask": subtask,
        "response": response,
        "estimated_tokens": estimated_tokens,
        "estimated_cost": round(total_cost, 6),
    }
