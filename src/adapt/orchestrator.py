"""The main loop. Owns the episode state: current round number, whose turn it is
(Red or Blue), the active RoEContract, and a rolling history of the episode so far.

Calls into `routing.model_router` -> `agents.*` -> `verification.triage_gateway` ->
`memory.csim_store`, in that order, each round. This is the one file that "knows"
the whole system shape -- everyone else is a component it calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.schemas import AttackTechnique, ExploitAttempt, RoEContract, Verdict


@dataclass
class EpisodeState:
    round_number: int = 0
    phase: str = "red"  # "red" or "blue"
    contract: RoEContract | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    verdicts: list[str] = field(default_factory=list)


class Orchestrator:
    """Drives one full episode: round #, whose turn, active contract, history."""

    def __init__(self, contract: RoEContract, model_client: Any = None) -> None:
        self.state = EpisodeState(contract=contract)
        self.model_client = model_client

    def run_episode(self, n_rounds: int) -> EpisodeState:
        """Run the episode loop for n_rounds, alternating Red/Blue turns."""
        from adapt.agents.blue_team.patch_synthesizer import synthesize_patch
        from adapt.agents.blue_team.telemetry_ingest import ingest_events
        from adapt.agents.blue_team.yara_rule_generator import generate_yara_rule
        from adapt.agents.red_team.exploit_generator import generate_exploit
        from adapt.agents.red_team.payload_mutator import mutate
        from adapt.contract.constraint_enforcer import check
        from adapt.mitre.attack_mapper import map_to_technique
        from adapt.routing.model_router import route
        from adapt.utils.metrics import Metrics
        from adapt.verification.triage_gateway import triage

        metrics = Metrics()
        contract = self.state.contract
        last_exploit: ExploitAttempt | None = None
        last_verdict: Verdict | None = None

        for r in range(1, n_rounds + 1):
            self.state.round_number = r

            # --- RED PHASE ---
            self.state.phase = "red"
            subtask = contract.revisable_strategy.objective if contract else "attack target"
            techniques = map_to_technique(subtask)
            technique = (
                techniques[0]
                if techniques
                else AttackTechnique(
                    technique_id="T1558",
                    name="Steal or Forge Kerberos Tickets",
                    tactic="credential-access",
                )
            )

            # If previous round was PIVOT, mutate previous payload
            if last_verdict is Verdict.PIVOT and last_exploit is not None:
                exploit = mutate(last_exploit, technique_id=technique.technique_id, model_client=self.model_client)
            else:
                handle = route(subtask, technique=technique)
                exploit = generate_exploit(
                    graphs={},
                    technique=technique,
                    subtask=subtask,
                    model_client=self.model_client,
                )

            last_exploit = exploit

            # Check action against RoE contract
            action = {"tool": "exploit_execute", "target_host": "sandbox-target", "payload": exploit.payload}
            enforcement = check(action, contract) if contract else None

            if enforcement and not enforcement.allowed:
                red_outcome = {
                    "round_number": r,
                    "contract_violation": True,
                    "reason": enforcement.reason,
                    "blocked_action": action,
                }
            else:
                red_outcome = {
                    "round_number": r,
                    "success": True,
                    "exploit": exploit,
                    "actions": [action],
                }

            # --- BLUE PHASE ---
            self.state.phase = "blue"
            events = list(ingest_events())
            breach_context = {"round": r, "technique": technique.technique_id, "events": len(events)}
            patch = synthesize_patch(breach_context, {}, model_client=self.model_client)
            yara = generate_yara_rule(breach_context, model_client=self.model_client)

            blue_outcome = {
                "round_number": r,
                "success": True,
                "patch": {"file_path": patch.file_path, "diff": patch.diff, "description": patch.description},
                "yara": yara,
                "verified_criteria": contract.revisable_strategy.verification_criteria if contract else [],
            }

            # --- TRIAGE GATEWAY ---
            outcome = triage(red_outcome, blue_outcome, contract) if contract else None
            verdict = outcome.verdict if outcome else Verdict.PASS
            last_verdict = verdict
            self.state.verdicts.append(verdict.value)
            metrics.record_verdict(verdict.value)

            round_record = {
                "round": r,
                "red_outcome": red_outcome,
                "blue_outcome": blue_outcome,
                "verdict": verdict.value,
                "reason": outcome.reason if outcome else "",
            }
            self.state.history.append(round_record)

        return self.state
