"""Tests for `adapt.verification.triage_gateway`."""
import pytest

from adapt.verification.triage_gateway import triage


def test_triage_not_implemented():
    with pytest.raises(NotImplementedError):
        triage(red_outcome={}, blue_outcome={}, contract=None)
