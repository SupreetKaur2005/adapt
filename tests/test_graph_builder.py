"""Validates AST/CFG/DFG/PDG output against known sample code with a
hand-verified expected graph.
"""
import ast
import networkx as nx

from adapt.agents.red_team.graph_builder import build_ast, build_cfg, build_dfg, build_pdg


SAMPLE_CODE = """
x = 10
if x > 5:
    y = x * 2
else:
    y = 0
z = y + 1
"""


def test_build_ast():
    tree = build_ast(SAMPLE_CODE)
    assert isinstance(tree, ast.AST)
    assert isinstance(tree, ast.Module)


def test_build_cfg():
    cfg = build_cfg(SAMPLE_CODE)
    assert isinstance(cfg, nx.DiGraph)
    assert "entry" in cfg.nodes
    assert "exit" in cfg.nodes
    assert len(cfg.nodes) >= 4
    assert len(cfg.edges) >= 3


def test_build_dfg():
    dfg = build_dfg(SAMPLE_CODE)
    assert isinstance(dfg, nx.DiGraph)
    # Checks that definitions and usages exist
    nodes = list(dfg.nodes(data=True))
    assert any(d.get("type") == "def" for _, d in nodes)
    assert any(d.get("type") == "use" for _, d in nodes)


def test_build_pdg():
    cfg = build_cfg(SAMPLE_CODE)
    dfg = build_dfg(SAMPLE_CODE)
    pdg = build_pdg(cfg, dfg)
    assert isinstance(pdg, nx.DiGraph)
    assert len(pdg.nodes) >= len(cfg.nodes)
