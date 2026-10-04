"""Tests for `adapt.contract.contract_writer`."""
from adapt.contract.contract_writer import update_strategy


def test_update_strategy_builds_revisable_strategy():
    strategy = update_strategy("extract credentials from DC01", ["gained domain admin"])
    assert strategy.objective == "extract credentials from DC01"
    assert strategy.verification_criteria == ["gained domain admin"]
