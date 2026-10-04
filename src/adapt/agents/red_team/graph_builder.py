"""Builds all four program-analysis representations from target source: AST,
CFG, DFG, PDG (Python `ast`/`tree-sitter`, `networkx`).
"""
from __future__ import annotations

import ast
from typing import Any

import networkx as nx


def build_ast(source: str | ast.AST) -> ast.AST:
    """Parse source string into Python AST, or return if already an AST node."""
    if isinstance(source, ast.AST):
        return source
    if not isinstance(source, str):
        raise TypeError("source must be a string or ast.AST")
    return ast.parse(source)


def build_cfg(ast_tree: Any) -> nx.DiGraph:
    """Build a Control Flow Graph (CFG) from an AST node."""
    if isinstance(ast_tree, str):
        ast_tree = build_ast(ast_tree)

    graph = nx.DiGraph()
    if not isinstance(ast_tree, ast.AST):
        return graph

    entry_node = "entry"
    exit_node = "exit"
    graph.add_node(entry_node, type="entry", label="ENTRY")
    graph.add_node(exit_node, type="exit", label="EXIT")

    prev_node = entry_node
    body = getattr(ast_tree, "body", [ast_tree])
    for idx, stmt in enumerate(body):
        node_id = f"stmt_{idx}_{type(stmt).__name__}"
        label = ast.unparse(stmt) if hasattr(ast, "unparse") else type(stmt).__name__
        graph.add_node(node_id, type="statement", label=label, ast_node=stmt)
        graph.add_edge(prev_node, node_id, edge_type="control_flow")

        if isinstance(stmt, ast.If):
            then_id = f"{node_id}_then"
            graph.add_node(then_id, type="branch_then", label="then")
            graph.add_edge(node_id, then_id, edge_type="branch_true")

            if stmt.orelse:
                else_id = f"{node_id}_else"
                graph.add_node(else_id, type="branch_else", label="else")
                graph.add_edge(node_id, else_id, edge_type="branch_false")
        prev_node = node_id

    graph.add_edge(prev_node, exit_node, edge_type="control_flow")
    return graph


def build_dfg(ast_tree: Any) -> nx.DiGraph:
    """Build a Data Flow Graph (DFG) representing def-use chains from an AST."""
    if isinstance(ast_tree, str):
        ast_tree = build_ast(ast_tree)

    graph = nx.DiGraph()
    if not isinstance(ast_tree, ast.AST):
        return graph

    defs: dict[str, list[str]] = {}

    node_counter = 0
    for node in ast.walk(ast_tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            node_counter += 1
            def_id = f"def_{node_counter}_{getattr(node, 'lineno', 0)}"
            label = ast.unparse(node) if hasattr(ast, "unparse") else "assign"
            graph.add_node(def_id, type="def", label=label, ast_node=node)

            targets = getattr(node, "targets", [getattr(node, "target", None)])
            for t in targets:
                if isinstance(t, ast.Name):
                    defs.setdefault(t.id, []).append(def_id)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            node_counter += 1
            use_id = f"use_{node_counter}_{node.id}_{getattr(node, 'lineno', 0)}"
            graph.add_node(use_id, type="use", var_name=node.id, ast_node=node)
            if node.id in defs:
                for def_id in defs[node.id]:
                    graph.add_edge(def_id, use_id, edge_type="data_flow", var=node.id)

    return graph


def build_pdg(cfg: nx.DiGraph, dfg: nx.DiGraph) -> nx.DiGraph:
    """Build a Program Dependence Graph (PDG) combining control and data dependencies."""
    pdg = nx.DiGraph()

    for node, data in cfg.nodes(data=True):
        pdg.add_node(node, **data, layer="control")
    for u, v, data in cfg.edges(data=True):
        pdg.add_edge(u, v, **data, dependency="control")

    for node, data in dfg.nodes(data=True):
        if node not in pdg:
            pdg.add_node(node, **data, layer="data")
    for u, v, data in dfg.edges(data=True):
        pdg.add_edge(u, v, **data, dependency="data")

    return pdg
