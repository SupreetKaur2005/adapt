"""Tests for `adapt.contract.constraint_enforcer`."""
from adapt.contract.constraint_enforcer import check
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def _contract(**frozen_overrides) -> RoEContract:
    defaults = dict(
        intent="test episode",
        prohibited_subnets=["10.0.2.0/24", "dc02"],
        max_execution_time_s=60,
        absolute_rules=["never use rodc_dump"],
    )
    defaults.update(frozen_overrides)
    return RoEContract(
        frozen_constraints=FrozenConstraints(**defaults),
        revisable_strategy=RevisableStrategy(objective="test", verification_criteria=[]),
    )


def test_allowed_action_passes():
    result = check({"tool": "port_scan", "target_host": "ws01"}, _contract())
    assert result.allowed


def test_blocks_prohibited_subnet_by_cidr():
    result = check({"tool": "port_scan", "target_host": "10.0.2.5"}, _contract())
    assert not result.allowed
    assert "prohibited subnet" in result.reason


def test_blocks_prohibited_subnet_by_exact_host():
    result = check({"tool": "port_scan", "target_host": "dc02"}, _contract())
    assert not result.allowed


def test_blocks_banned_tool_rule():
    result = check({"tool": "rodc_dump", "target_host": "dc01"}, _contract())
    assert not result.allowed
    assert "absolute rule" in result.reason


def test_blocks_time_overrun():
    action = {"tool": "port_scan", "target_host": "ws01", "elapsed_time_s": 120}
    result = check(action, _contract(max_execution_time_s=60))
    assert not result.allowed
    assert "max_execution_time_s" in result.reason


def test_validate_action_delegates_to_check():
    contract = _contract()
    assert contract.validate_action({"tool": "port_scan", "target_host": "ws01"}) is True
    assert contract.validate_action({"tool": "rodc_dump", "target_host": "dc01"}) is False


def test_blocks_prohibited_with_port_and_url():
    contract = _contract()
    assert not check({"tool": "port_scan", "target_host": "10.0.2.5:8080"}, contract).allowed
    assert not check({"tool": "port_scan", "target_host": "http://10.0.2.5/endpoint"}, contract).allowed


def test_blocks_case_insensitive_host():
    contract = _contract()
    assert not check({"tool": "port_scan", "target_host": "DC02"}, contract).allowed


def test_blocks_nested_tool_args():
    contract = _contract()
    action = {"tool_name": "port_scan", "tool_args": {"target_host": "10.0.2.5"}}
    result = check(action, contract)
    assert not result.allowed
    assert "prohibited subnet" in result.reason

    banned_action = {"tool_name": "rodc_dump", "tool_args": {"target_host": "ws01"}}
    assert not check(banned_action, contract).allowed


def test_safe_on_empty_and_none_fields():
    contract = _contract()
    assert check({}, contract).allowed
    assert check({"target_host": None, "tool": None}, contract).allowed
    assert check({"target_host": "", "tool": ""}, contract).allowed
