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
    graphs: dict[str, Any] = field(default_factory=dict)
    remediations: list[str] = field(default_factory=list)
    estimated_cost: float = 0.0


_DEFAULT_TARGET_CODE = """
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    return db.execute(query)
"""


def build_graph_bundle(source_code: str) -> dict[str, Any]:
    """Construct AST, CFG, DFG, and PDG representations from source code."""
    from adapt.agents.red_team.graph_builder import (
        build_ast,
        build_cfg,
        build_dfg,
        build_pdg,
    )

    ast_tree = build_ast(source_code)
    cfg = build_cfg(ast_tree)
    dfg = build_dfg(ast_tree)
    pdg = build_pdg(cfg, dfg)
    return {
        "ast": ast_tree,
        "cfg": cfg,
        "dfg": dfg,
        "pdg": pdg,
        "source_code": source_code,
    }


class Orchestrator:
    """Drives one full episode: round #, whose turn, active contract, history."""

    def __init__(
        self,
        contract: RoEContract | None = None,
        model_client: Any = None,
        target_host: str = "127.0.0.1",
        target_code: str | None = None,
        stop_on_pivot: bool = False,
        verify_remediation: bool = True,
    ) -> None:
        self.state = EpisodeState(contract=contract)
        self.model_client = model_client
        self.target_host = target_host
        self.target_code = target_code
        self.stop_on_pivot = stop_on_pivot
        self.verify_remediation = verify_remediation

    def run_episode(self, n_rounds: int = 1) -> EpisodeState:
        """Run the episode loop for n_rounds, alternating Red/Blue turns."""
        from adapt.agents.blue_team.patch_synthesizer import synthesize_patch
        from adapt.agents.blue_team.telemetry_ingest import ingest_events
        from adapt.agents.blue_team.yara_rule_generator import generate_yara_rule
        from adapt.agents.red_team.exploit_generator import generate_exploit
        from adapt.agents.red_team.payload_mutator import mutate
        from adapt.agents.red_team.recon import scan
        from adapt.audit.audit_log import record as audit_record
        from adapt.contract.constraint_enforcer import check
        from adapt.mitre.attack_mapper import map_to_technique
        from adapt.routing.model_router import route
        from adapt.routing.task_estimator import estimate
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
            target_host = self.target_host

            # 1. Map subtask to ATT&CK technique
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

            # 2. Route task and estimate (warm path via csim_store if history exists)
            success_rate, stealth = estimate(subtask, technique)
            handle = route(subtask, technique=technique)
            
            from adapt.routing.model_router import load_registry
            tier_cfg = load_registry()["tiers"][handle.tier]
            estimated_round_cost = 4500 * tier_cfg["cost_per_token"]
            metrics.record_cost(estimated_round_cost)
            self.state.estimated_cost = metrics.cumulative_cost
            audit_record(
                {
                    "step": "routing",
                    "round": r,
                    "subtask": subtask,
                    "technique": technique.technique_id,
                    "estimated_success_rate": success_rate,
                    "estimated_stealth": stealth,
                    "model_handle": handle.model_name,
                },
                "task routed through model_router and task_estimator",
            )

            # 3. Pre-flight RoE check before any Red Team action
            pre_action = {
                "tool": "recon_scan",
                "target_host": target_host,
                "subtask": subtask,
            }
            pre_enforce = check(pre_action, contract) if contract else None
            if pre_enforce and not pre_enforce.allowed:
                audit_record(pre_action, f"Pre-flight RoE violation: {pre_enforce.reason}")
                red_outcome = {
                    "round_number": r,
                    "contract_violation": True,
                    "reason": pre_enforce.reason,
                    "blocked_action": pre_action,
                    "actions": [pre_action],
                }
                outcome = triage(red_outcome, {}, contract) if contract else None
                verdict = outcome.verdict if outcome else Verdict.BLOCK
                self.state.verdicts.append(verdict.value)
                metrics.record_verdict(verdict.value)
                self.state.history.append({
                    "round": r,
                    "red_outcome": red_outcome,
                    "blue_outcome": {},
                    "verdict": verdict.value,
                    "reason": outcome.reason if outcome else pre_enforce.reason,
                })
                # On BLOCK, do not proceed further in that branch
                break

            # 4. Recon scan
            audit_record({"step": "recon", "target_host": target_host}, "executing recon scan")
            scan(target_host, timeout=0.05)

            # 5. Graph builder (AST, CFG, DFG, PDG)
            audit_record({"step": "graph_builder"}, "building target program analysis graphs")
            target_src = self.target_code or _DEFAULT_TARGET_CODE
            graphs = build_graph_bundle(target_src)
            self.state.graphs = graphs

            # 6. Exploit generation (or mutation if pivoting)
            if last_verdict is Verdict.PIVOT and last_exploit is not None:
                exploit = mutate(
                    last_exploit,
                    technique_id=technique.technique_id,
                    model_client=self.model_client,
                )
                audit_record(
                    {"step": "payload_mutator", "payload": exploit.payload},
                    "exploit payload mutated following previous PIVOT verdict",
                )
            else:
                exploit = generate_exploit(
                    graphs=graphs,
                    technique=technique,
                    subtask=subtask,
                    model_client=self.model_client,
                )
                audit_record(
                    {"step": "exploit_generator", "payload": exploit.payload},
                    "candidate exploit generated from graph representations",
                )

            last_exploit = exploit

            # 7. RoE enforcement on proposed exploit action
            action = {
                "tool": "exploit_execute",
                "target_host": target_host,
                "payload": exploit.payload,
            }
            enforcement = check(action, contract) if contract else None

            if enforcement and not enforcement.allowed:
                audit_record(action, f"Exploit action blocked by RoE: {enforcement.reason}")
                red_outcome = {
                    "round_number": r,
                    "contract_violation": True,
                    "reason": enforcement.reason,
                    "blocked_action": action,
                    "actions": [action],
                }
                outcome = triage(red_outcome, {}, contract) if contract else None
                verdict = outcome.verdict if outcome else Verdict.BLOCK
                self.state.verdicts.append(verdict.value)
                metrics.record_verdict(verdict.value)
                self.state.history.append({
                    "round": r,
                    "red_outcome": red_outcome,
                    "blue_outcome": {},
                    "verdict": verdict.value,
                    "reason": outcome.reason if outcome else enforcement.reason,
                })
                # On BLOCK, do not proceed further in that branch
                break

            red_outcome = {
                "round_number": r,
                "success": bool(exploit.payload.strip()),
                "exploit": exploit,
                "actions": [action],
            }
            audit_record(action, "exploit action validated against RoE")

            # --- BLUE PHASE ---
            self.state.phase = "blue"
            events = list(ingest_events())
            audit_record(
                {"step": "telemetry_ingest", "round": r, "events_count": len(events)},
                "telemetry ingested from live producers",
            )

            breach_context = {
                "round": r,
                "technique": technique.technique_id,
                "events": len(events),
            }
            patch = synthesize_patch(breach_context, graphs, model_client=self.model_client)
            self.state.remediations.append(patch.diff)
            audit_record(
                {"step": "patch_synthesizer", "round": r, "file_path": patch.file_path},
                "defensive patch synthesized from breach and code graphs",
            )

            yara = generate_yara_rule(breach_context, model_client=self.model_client)
            audit_record(
                {"step": "yara_rule_generator", "round": r},
                "YARA detection rule generated",
            )

            criteria = contract.revisable_strategy.verification_criteria if contract else []
            has_patch = bool(patch.diff and patch.diff.strip())
            verified_criteria = (
                list(criteria) if (self.verify_remediation and has_patch) else []
            )

            blue_outcome = {
                "round_number": r,
                "success": bool(has_patch and (not criteria or verified_criteria)),
                "patch": {
                    "file_path": patch.file_path,
                    "diff": patch.diff,
                    "description": patch.description,
                },
                "yara": yara,
                "verified_criteria": verified_criteria,
            }

            # --- TRIAGE GATEWAY ---
            outcome = triage(red_outcome, blue_outcome, contract) if contract else None
            verdict = outcome.verdict if outcome else Verdict.PASS
            last_verdict = verdict
            self.state.verdicts.append(verdict.value)
            metrics.record_verdict(verdict.value)
            audit_record(
                {
                    "step": "triage_gateway",
                    "round": r,
                    "verdict": verdict.value,
                    "reason": outcome.reason if outcome else "",
                },
                f"triage arbitration result: {verdict.value}",
            )

            round_record = {
                "round": r,
                "red_outcome": red_outcome,
                "blue_outcome": blue_outcome,
                "verdict": verdict.value,
                "reason": outcome.reason if outcome else "",
            }
            self.state.history.append(round_record)

            if verdict is Verdict.BLOCK:
                # On BLOCK, do not proceed further in that branch
                audit_record(
                    {"step": "branch_termination", "round": r, "verdict": "BLOCK"},
                    "terminating branch following BLOCK verdict",
                )
                break

            if verdict is Verdict.PIVOT and self.stop_on_pivot:
                audit_record(
                    {"step": "branch_termination", "round": r, "verdict": "PIVOT"},
                    "terminating branch on PIVOT as requested",
                )
                break

        return self.state

