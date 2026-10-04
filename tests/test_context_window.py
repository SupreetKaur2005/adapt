"""Tests for `adapt.context.context_window`."""
from adapt.context.context_manager import Context
from adapt.context.context_window import fit_to_window


def test_fit_to_window_keeps_most_recent_history():
    # Each turn costs ~10 estimated tokens; a 35-token budget fits 3 of the
    # 10 turns, so some but not all must be dropped -- and the most recent
    # one must survive.
    history = [{"role": "observation", "content": "x" * 40} for _ in range(10)]
    context = Context(system_prompt="sys", history=history, contract_state={}, tool_schemas=[])

    trimmed = fit_to_window(context, max_tokens=35)

    assert 0 < len(trimmed.history) < len(history)
    assert trimmed.history[-1] == history[-1]


def test_fit_to_window_keeps_everything_when_it_fits():
    history = [{"role": "observation", "content": "short"}]
    context = Context(system_prompt="sys", history=history, contract_state={}, tool_schemas=[])

    trimmed = fit_to_window(context, max_tokens=10_000)

    assert trimmed.history == history
