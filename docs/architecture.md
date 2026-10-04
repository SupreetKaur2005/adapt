# A.D.A.P.T. Architecture

## Overview

A.D.A.P.T. runs episodes of adversarial simulation between a Red Team agent and
a Blue Team agent, governed by a White Team-authored Rules-of-Engagement
contract, with every decision routed across local LLM tiers rather than a
single frontier model.

## Episode loop (`src/adapt/orchestrator.py`)

Each round:

1. `routing.model_router` picks a model tier for the current subtask, scored by
   `routing.cuv_calculator` (CUV = success x stealth / cost x time), using
   `routing.task_estimator` for the inputs it can't observe directly (warm from
   `memory.csim_store`, cold-start from a fixed heuristic table).
2. The active agent (`agents.red_team.*` or `agents.blue_team.*`) runs its
   ReAct loop (`agents.base_agent`) against the routed model, calling sandbox
   tools.
3. Every proposed action passes through `contract.constraint_enforcer.check`
   against the active `RoEContract`. A `BLOCKED` result is written to
   `audit.audit_log` and the sandbox is reset.
4. `verification.outcome_classifier` determines whether Red/Blue actually
   succeeded; `verification.triage_gateway.triage` turns that into a
   `PASS` / `BLOCK` / `PIVOT` verdict.
5. On `PASS`, the exploit/patch pair is committed to `memory.csim_store` (the
   "vaccine registry"), improving future `task_estimator` warm estimates.
   On `PIVOT`, `agents.red_team.payload_mutator` mutates the next attempt,
   seeded by Atomic Red Team playbooks.

## MITRE ATT&CK mapping (`src/adapt/mitre/`)

Subtasks are mapped onto ATT&CK techniques (`attack_mapper.map_to_technique`)
against the filtered technique set defined by `skill_space.SkillSpace`
(`S_cyber`), loaded from the local STIX bundle via
`datasets/mitre_attack_loader.py`.

## Sandbox (`src/adapt/sandbox/`)

A Mininet-built network fabric (`mininet_topology.py`) hosts a simulated AD
domain (`targets/ad_lab_config.py`) and seeded-vulnerability targets
(`targets/vulnerable_apps/`). Telemetry comes from eBPF probes and
Sysmon-for-Linux (`telemetry_producers/`), consumed by
`agents.blue_team.telemetry_ingest`.

## Baselines and evaluation

`baseline/` provides two points of comparison -- a single monolithic local
model with no routing, and a traditional non-agentic scanner -- plus harness
adapters for the Cybench and NYU CTF Bench task sets. `eval/cost_analysis.py`
computes the actual cost delta between routed and baseline runs from
`utils.metrics` output; `eval/run_comparison.py` drives all three conditions
against the same sandbox targets.

See [`../ADAPT_File_Details.md`](../ADAPT_File_Details.md) for the complete
file-by-file spec.
