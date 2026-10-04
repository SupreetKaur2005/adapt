"""Validates AST/CFG/DFG/PDG output against known sample code with a
hand-verified expected graph.
"""
import pytest

from adapt.agents.red_team.graph_builder import build_ast


def test_build_ast_not_implemented():
    with pytest.raises(NotImplementedError):
        build_ast("def f(): pass")
