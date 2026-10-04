# A.D.A.P.T. — Team Work-Breakdown Plan

**Team:** Aniket (Red Team) · Supreet (Blue Team) · Suraj (White Team) · Khushi (LLM / Sandbox / Graph / CSIM / Test)

This plan assigns every file in [`ADAPT_File_Details.md`](../ADAPT_File_Details.md) to a phase and an owner, so the four of us can work in parallel without blocking each other.

**Status: the entire common base (Phase 0 + Phase 1) is done, tested, and merged to `main`. Everyone is unblocked to start Phase 2 now.**

## Phase 0 + 1 — Common base (done, on `main`)

Nobody needs to touch these; they're the foundation everyone else builds on. (Phase 1 was originally earmarked for Suraj/Khushi but got built ahead of schedule so the whole team could start Phase 2 immediately — no need to redo any of it.)

| Area | Files | Status |
|---|---|---|
| Scaffold | full tree, `pyproject.toml`, `config/*.yaml`, `docker/` skeleton, `docs/` | Done |
| Typed models | `src/adapt/schemas.py` | Done |
| RoE contract | `contract/roe_contract.py`, `contract/constraint_enforcer.py`, `contract/contract_writer.py` | Done + tested |
| Audit trail | `audit/audit_log.py` | Done + tested |
| TOPAZ routing core | `routing/cuv_calculator.py`, `routing/task_estimator.py`, `routing/model_router.py`, `routing/model_scheduler.py` | Done + tested |
| Utils | `utils/logger.py`, `utils/metrics.py` | Done (trivial) |
| Shared ReAct loop | `agents/base_agent.py` | Done + tested |
| Local model clients | `routing/model_clients/ollama_client.py`, `hf_client.py` | Done + tested |
| Prompt/context assembly | `context/context_manager.py`, `context_window.py`, `prompt_templates.py` | Done + tested |
| Sandbox control | `sandbox/container_manager.py`, `sandbox/mininet_topology.py` (minimal version) | Done + tested |

37 tests passing on `main`. Everything above is real logic, not stubs — see the module docstrings for exactly what each does.

## Phase 2 — Per-person ownership (parallel, start now)

### Aniket — Red Team
`src/adapt/agents/red_team/` (everything except `graph_builder.py`, which Khushi owns):
- `recon.py`
- `exploit_generator.py`
- `payload_mutator.py`
- `tools/port_scan_tool.py`, `tools/payload_execute_tool.py`, `tools/kerberoast_tool.py`, `tools/asrep_roast_tool.py`, `tools/rodc_dump_tool.py`, `tools/tool_schema.py`

Common base is done, so you're unblocked today. Soft dependencies to wire in later, not blockers to starting: `mitre/attack_mapper.py` (Suraj) for technique-aware generation, `graph_builder.py` (Khushi) for `exploit_generator.py`'s input.

### Supreet — Blue Team
`src/adapt/agents/blue_team/`:
- `telemetry_ingest.py`
- `patch_synthesizer.py`
- `yara_rule_generator.py`
- `tools/telemetry_query_tool.py`, `tools/patch_deploy_tool.py`, `tools/tool_schema.py`

Common base is done, so you're unblocked today. Soft dependency to wire in later: `sandbox/telemetry_producers/` (Khushi) for real event input.

### Suraj — White Team / Argus
Contract work already done. Remaining governance layer:
- `mitre/attack_mapper.py`, `mitre/skill_space.py` — defines the `S_cyber` scope the contract and CUV routing score against.
- `verification/triage_gateway.py`, `verification/outcome_classifier.py` — the `PASS`/`BLOCK`/`PIVOT` arbiter.

### Khushi — LLM / Sandbox / Graph / CSIM / Test
- **Sandbox** (remaining pieces beyond the done minimal version): `network_isolator.py`, `targets/ad_lab_config.py`, `targets/vulnerable_apps/`, `telemetry_producers/sysmon_linux_config.py`, `telemetry_producers/ebpf_probes/`, and firming up `docker/` + `scripts/reset_sandbox.sh`.
- **Graph**: `agents/red_team/graph_builder.py` (AST/CFG/DFG/PDG) — filed under `red_team/` on disk, owned by Khushi; Aniket consumes its output.
- **CSIM / vector DB**: `memory/csim_store.py`, `memory/embedding.py`, `memory/vector_db_client.py`. Note: `task_estimator.py`'s warm path already calls `csim_store.query_similar` and gracefully falls back to cold-start today, so this can land whenever — routing upgrades automatically, no coordination needed.
- **Datasets** (generic data-plumbing, not team-specific): all 6 files in `datasets/`.
- **Test / benchmarking**: all of `baseline/` (4 files) and `eval/` (3 files), plus `scripts/run_baseline.py`, `scripts/pull_local_models.sh`; and filling out `tests/` coverage as each module above lands. (Each owner should still add tests for their *own* modules as they go — Khushi's job is closing gaps and the cross-cutting harness, not writing every test alone.)

## Phase 3 — Integration (collaborative, after Phase 2 lands)

- `src/adapt/orchestrator.py` — calls into every stream in sequence; needs interfaces from all four, so it's finished last. Suggest Khushi + Suraj lead (routing, contract, and verification are the modules it touches most).
- First full `scripts/run_simulation.py` run end-to-end against the live sandbox.
- `eval/run_comparison.py` + `eval/cost_analysis.py` — the real 60–80% cost-savings number, only meaningful once routing, baselines, and a real sandbox exist together.

## Dependency summary (who blocks whom)

```
Common base (done) ──┬──────────────┬──────────────┬──────────────┐
                      ↓              ↓              ↓              ↓
              Aniket (Red)   Supreet (Blue)  Suraj (mitre,   Khushi (graph,
                                              verification)  CSIM, datasets,
                                                              baselines, eval)
              all four start in parallel today — no one is blocked
                      ↓              ↓              ↓              ↓
                      └──────────────┴──────────────┴──────────────┘
                                          ↓
                      Phase 3: orchestrator.py + full run + cost analysis
```
