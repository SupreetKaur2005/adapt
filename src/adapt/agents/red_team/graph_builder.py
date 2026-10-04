"""Builds all four program-analysis representations from target source: AST,
CFG, DFG, PDG (Python `ast`/`tree-sitter`, `networkx`).
"""
from __future__ import annotations

from typing import Any

import networkx as nx


def build_ast(source: str) -> Any:
    """Python `ast` module, or `tree-sitter` for other languages."""
    raise NotImplementedError


def build_cfg(ast_tree: Any) -> nx.DiGraph:
    raise NotImplementedError


def build_dfg(ast_tree: Any) -> nx.DiGraph:
    raise NotImplementedError


def build_pdg(cfg: nx.DiGraph, dfg: nx.DiGraph) -> nx.DiGraph:
    raise NotImplementedError
