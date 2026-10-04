"""Given a detected breach + its graph representation, generates a code-level patch."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Patch:
    file_path: str
    diff: str
    description: str


class _ModelClient:
    def generate(self, model: str, prompt: str, **kwargs: Any) -> str: ...


def _summarize_graphs(graphs: dict[str, Any]) -> str:
    if not graphs:
        return "(no graph data available)"
    parts = []
    for name, graph in graphs.items():
        nodes = getattr(graph, "nodes", None)
        size = len(nodes) if nodes is not None else "?"
        parts.append(f"{name}: {size} nodes")
    return ", ".join(parts)


def synthesize_patch(
    breach: dict, graphs: dict[str, Any], model_client: _ModelClient | None = None
) -> Patch:
    from adapt.routing.model_router import route
    from adapt.routing.model_scheduler import acquire

    subtask = "synthesize patch for breach"
    handle = route(subtask)

    if model_client is None:
        from adapt.routing.model_clients.ollama_client import OllamaClient

        model_client = OllamaClient()

    prompt = (
        "Target code analysis summary:\n"
        f"{_summarize_graphs(graphs)}\n\n"
        f"Breach details: {breach}\n"
        "Generate a code-level patch to fix the vulnerability. "
        "Respond with a file path, a description, and the diff."
    )

    with acquire(handle):
        response = model_client.generate(handle.model_name, prompt).strip()

    file_path, diff, description = _parse_patch_response(response)
    return Patch(
        file_path=file_path,
        diff=diff,
        description=description,
    )


def _parse_patch_response(response: str) -> tuple[str, str, str]:
    file_path = "unknown"
    description = "Auto-generated patch"
    diff = response

    for line in response.splitlines():
        line_stripped = line.strip()
        lower = line_stripped.lower()
        if lower.startswith("file:") or lower.startswith("filepath:"):
            parsed_path = line_stripped.split(":", 1)[1].strip().strip("`")
            if parsed_path:
                file_path = parsed_path
        elif lower.startswith("description:"):
            parsed_desc = line_stripped.split(":", 1)[1].strip()
            if parsed_desc:
                description = parsed_desc

    if "```diff" in response:
        diff = response.split("```diff", 1)[1].split("```", 1)[0].strip()
    elif "```" in response:
        code_block = response.split("```", 1)[1].split("```", 1)[0].strip()
        if "---" in code_block or "+++" in code_block or "@@" in code_block:
            diff = code_block

    return file_path, diff, description
