"""Tests for `adapt.contract.constraint_enforcer`."""
import pytest

from adapt.contract.constraint_enforcer import check


def test_check_not_implemented():
    with pytest.raises(NotImplementedError):
        check(action={}, contract=None)
