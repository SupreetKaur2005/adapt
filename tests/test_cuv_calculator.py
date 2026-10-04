"""Tests for `adapt.routing.cuv_calculator`."""
import pytest

from adapt.routing.cuv_calculator import compute_cuv


def test_compute_cuv_not_implemented():
    with pytest.raises(NotImplementedError):
        compute_cuv("subtask", technique=None, candidate_model="mistral:7b")
