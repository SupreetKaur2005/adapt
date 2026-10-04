"""The main loop. Owns the episode state: current round number, whose turn it is
(Red or Blue), the active RoEContract, and a rolling history of the episode so far.

Calls into `routing.model_router` -> `agents.*` -> `verification.triage_gateway` ->
`memory.csim_store`, in that order, each round. This is the one file that "knows"
the whole system shape -- everyone else is a component it calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from adapt.schemas import RoEContract


@dataclass
class EpisodeState:
    round_number: int = 0
    phase: str = "red"  # "red" or "blue"
    contract: RoEContract | None = None
    history: list[dict] = field(default_factory=list)


class Orchestrator:
    """Drives one full episode: round #, whose turn, active contract, history."""

    def __init__(self, contract: RoEContract) -> None:
        self.state = EpisodeState(contract=contract)

    def run_episode(self, n_rounds: int) -> EpisodeState:
        """Run the episode loop for n_rounds, alternating Red/Blue turns."""
        raise NotImplementedError
