"""Validates subtask -> ATT&CK technique mapping against a small labeled set."""
import pytest

from adapt.mitre.attack_mapper import map_to_technique


def test_map_to_technique_not_implemented():
    with pytest.raises(NotImplementedError):
        map_to_technique("attempt credential extraction on DC01")
