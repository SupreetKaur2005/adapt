"""Tests for `adapt.memory.csim_store`."""
import pytest

from adapt.memory.csim_store import query_similar


def test_query_similar_not_implemented():
    with pytest.raises(NotImplementedError):
        query_similar("some subtask")
