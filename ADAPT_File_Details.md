# A.D.A.P.T. — File-by-File Functional Spec

adapt/
├── README.md
├── pyproject.toml                   # + stix2, networkx, mininet, impacket, chromadb, ollama-python
├── .env.example                     # local endpoints only (Ollama)
│
├── config/
│   ├── model_registry.yaml          # local-only tiers (Mistral 7B/Llama 3.3 -> Qwen3.5/Gemma 4 -> DeepSeek V4-Flash)
│   ├── roe_contract_schema.yaml     # TWO sections: frozen_constraints, revisable_strategy
│   ├── sandbox_topology.yaml        # Mininet topology + AD lab layout
│   └── mitre_attack_config.yaml     # NEW — path/version of the local STIX bundle, S_cyber skill taxonomy
│
├── datasets/                        # ── NEW top-level: slide 5's dataset table, one loader each ──
│   ├── mitre_attack_loader.py       # loads MITRE ATT&CK STIX via the `stix2` library
│   ├── atomic_redteam_loader.py     # Atomic Red Team playbooks -> bootstraps Red Team mutation pipeline
│   ├── kaggle_threat_logs_loader.py # 6M+ synthetic logs, Blue Team classification baseline
│   ├── ebpf_traffic_loader.py       # ground-truth container-isolation test data
│   ├── splunk_ad_kerberos_loader.py # Event ID 4769/4104 — real Kerberoasting/AD patterns
│   └── impacket_trace_generator.py  # synthesizes AD attack pcaps via Impacket inside Mininet
│
├── docker/
│   ├── docker-compose.yml           # sandbox containers + Ollama service
│   ├── Dockerfile.sandbox
│   └── Dockerfile.telemetry
│
├── src/adapt/
│   ├── orchestrator.py              # episode state machine: round #, whose turn, current contract, history
│   │
│   ├── contract/                    # ── White Team / Argus ──
│   │   ├── roe_contract.py          # K_t = (I, O_t, C_t, V_t) split into FrozenConstraints + RevisableStrategy
│   │   ├── contract_writer.py       # White Team drafts/updates the revisable tier only
│   │   └── constraint_enforcer.py   # single enforcement point (v2 had this duplicated — fixed)
│   │
│   ├── mitre/                       # ── NEW: ATT&CK skill-space mapping ──
│   │   ├── attack_mapper.py         # maps a subtask description onto MITRE ATT&CK techniques (S_cyber)
│   │   └── skill_space.py           # the S_cyber taxonomy object CUV scores against
│   │
│   ├── routing/                     # ── TOPAZ ──
│   │   ├── cuv_calculator.py        # CUV = (success_rate × stealth) / (cost/token × exec_time), keyed by ATT&CK technique
│   │   ├── task_estimator.py        # estimates success-rate/stealth from CSIM history (cold-start heuristic pre-data)
│   │   ├── model_router.py          # routes across local tiers only
│   │   ├── model_scheduler.py       # queues GPU access across agents so local models don't collide
│   │   └── model_clients/
│   │       ├── ollama_client.py
│   │       └── hf_client.py
│   │
│   ├── context/
│   │   ├── context_manager.py
│   │   ├── context_window.py        # trims history to fit small local-model context windows
│   │   └── prompt_templates.py
│   │
│   ├── agents/
│   │   ├── base_agent.py            # ── NEW: shared ReAct loop (Thought -> Action -> Observation) ──
│   │   │
│   │   ├── red_team/
│   │   │   ├── recon.py
│   │   │   ├── graph_builder.py     # builds AST + CFG + DFG + PDG (ast/tree-sitter, networkx)
│   │   │   ├── exploit_generator.py # consumes graphs, proposes exploits
│   │   │   ├── payload_mutator.py
│   │   │   └── tools/
│   │   │       ├── port_scan_tool.py
│   │   │       ├── payload_execute_tool.py
│   │   │       ├── kerberoast_tool.py     # NEW — Event ID 4769-style attack, per dataset slide
│   │   │       ├── asrep_roast_tool.py    # NEW
│   │   │       ├── rodc_dump_tool.py      # NEW — RODC credential dumping
│   │   │       └── tool_schema.py
│   │   │
│   │   └── blue_team/
│   │       ├── telemetry_ingest.py
│   │       ├── patch_synthesizer.py
│   │       ├── yara_rule_generator.py
│   │       └── tools/
│   │           ├── telemetry_query_tool.py
│   │           ├── patch_deploy_tool.py
│   │           └── tool_schema.py
│   │
│   ├── verification/
│   │   ├── triage_gateway.py        # PASS / BLOCK / PIVOT
│   │   └── outcome_classifier.py
│   │
│   ├── memory/                      # ── CSIM ──
│   │   ├── csim_store.py
│   │   ├── embedding.py             # local embedding model, not an API
│   │   └── vector_db_client.py      # Chroma, fully local
│   │
│   ├── sandbox/
│   │   ├── container_manager.py
│   │   ├── network_isolator.py
│   │   ├── mininet_topology.py      # NEW — builds the network fabric Impacket traces run over
│   │   ├── targets/                 # NEW — what Red Team actually attacks
│   │   │   ├── vulnerable_apps/     # seeded-CVE web/services targets
│   │   │   └── ad_lab_config.py     # simulated AD domain + Kerberos setup
│   │   └── telemetry_producers/     # NEW — what generates the events Blue Team ingests
│   │       ├── ebpf_probes/
│   │       └── sysmon_linux_config.py
│   │
│   ├── schemas.py                   # NEW — RoEContract, ExploitAttempt, TriageOutcome, CUVScore as typed models
│   │
│   ├── audit/
│   │   └── audit_log.py             # NEW — persists every BLOCK event with cause, for the safety claim
│   │
│   └── utils/
│       ├── logger.py
│       └── metrics.py               # cost-savings + PASS/BLOCK/PIVOT rate tracking
│
├── baseline/                        # ── NEW: PERT step 14 ──
│   ├── baseline_llm.py              # single monolithic-LLM baseline (no routing, no governance)
│   ├── baseline_scanner.py          # traditional static/dynamic scanner baseline
│   ├── cybench_adapter.py           # benchmark harness against Cybench
│   └── nyu_ctf_adapter.py           # benchmark harness against NYU CTF Bench
│
├── eval/                            # ── NEW: PERT step 15 ──
│   ├── run_comparison.py            # routed vs baseline, produces the actual cost delta
│   ├── cost_analysis.py             # this is what backs your 60–80% conclusion number
│   └── results_dashboard.py
│
├── tests/
│   ├── test_cuv_calculator.py
│   ├── test_attack_mapper.py        # NEW
│   ├── test_triage_gateway.py
│   ├── test_constraint_enforcer.py
│   ├── test_csim_store.py
│   ├── test_graph_builder.py        # AST/CFG/DFG/PDG correctness on sample code
│   └── conftest.py                  # mocks local model calls so CI doesn't need a GPU
│
├── scripts/
│   ├── run_simulation.py
│   ├── run_baseline.py
│   ├── pull_local_models.sh
│   └── reset_sandbox.sh
│
├── data/
│   ├── csim_registry/
│   ├── sample_exploits/
│   └── raw_datasets/                # cached MITRE STIX, Atomic RT, Kaggle logs, Splunk AD data, etc.
│
└── docs/
    ├── architecture.md
    └── roe_contract_spec.md
    
For each file: what it does, key classes/functions, inputs → outputs, and what it talks to. Use this as the actual spec when you sit down to write each module.

---

## config/

**`model_registry.yaml`** — Static config, not code. Lists each routing tier (lightweight/mid/heavy) with the local model name, Ollama tag, approximate cost-per-token (even local models can carry a compute-cost proxy), and context window size. `model_router.py` reads this at startup.

**`roe_contract_schema.yaml`** — Defines the shape of `K_t` as two blocks: `frozen_constraints` (immutable once set — prohibited subnets, max execution time, absolute rules) and `revisable_strategy` (objective, current operational target — can change each round). `roe_contract.py` validates against this schema.

**`sandbox_topology.yaml`** — Mininet host/link definitions: number of hosts, the AD domain controller node, subnet layout, which hosts are "in scope" per the RoE contract.

**`mitre_attack_config.yaml`** — Path to the local STIX bundle file, ATT&CK version pinned, and the subset of tactics/techniques relevant to your scope (you don't need all ~600 techniques — probably a filtered list matching what Atomic Red Team playbooks cover).

---

## datasets/

**`mitre_attack_loader.py`** — Loads the ATT&CK STIX bundle via the `stix2` library. Key function: `load_attack_techniques() -> list[AttackTechnique]`. Output feeds `mitre/skill_space.py`.

**`atomic_redteam_loader.py`** — Parses Atomic Red Team's YAML test definitions from the cloned repo. Key function: `load_playbooks(technique_id: str) -> list[AtomicTest]`. Used by `payload_mutator.py` to seed realistic attack variants rather than generating exploits from nothing.

**`kaggle_threat_logs_loader.py`** — Loads the 6M+ row synthetic log dataset, returns a pandas/polars DataFrame. Used to pretrain or sanity-check Blue Team's classification behavior before it ever sees live sandbox telemetry.

**`ebpf_traffic_loader.py`** — Loads the labeled eBPF/XDP traffic dataset. Used as ground truth in `test_graph_builder.py`-style tests to confirm the sandbox's container isolation is actually working (i.e., no traffic escapes that shouldn't).

**`splunk_ad_kerberos_loader.py`** — Parses the Splunk-format AD attack logs (Event ID 4769 Kerberos ticket requests, Event ID 4104 PowerShell block logs). Key function: `load_kerberos_events() -> list[ADEvent]`. Feeds both Red Team's `kerberoast_tool.py` (what a realistic attack sequence looks like) and Blue Team's detection logic (what to flag).

**`impacket_trace_generator.py`** — Not a loader — actively generates new `.pcap` traces at runtime using Impacket, inside the Mininet sandbox. Key function: `generate_trace(attack_type: str, target_host: str) -> Path`. This is what actually produces AD-attack network traffic for Red Team to execute and Blue Team to observe, rather than replaying static files.

---

## src/adapt/orchestrator.py

The main loop. Owns the **episode state**: current round number, whose turn it is (Red or Blue), the active `RoEContract`, and a rolling history of the episode so far.

Key class: `Orchestrator` with:
- `run_episode(n_rounds: int)` — the top-level loop
- `EpisodeState` (dataclass) — round #, phase, contract reference, history log
- Calls into `model_router` → `agents/*` → `verification/triage_gateway` → `memory/csim_store`, in that order, each round.

This is the one file that "knows" the whole system shape — everyone else is a component it calls.

---

## src/adapt/contract/

**`roe_contract.py`** — Defines `RoEContract` as two nested objects:
- `FrozenConstraints` (I, C_t: intent + hard constraints) — set once at episode start, never mutated
- `RevisableStrategy` (O_t, V_t: current objective + verification criteria) — can be updated by White Team each round

Key method: `RoEContract.validate_action(action) -> bool` — the actual check every agent action passes through.

**`contract_writer.py`** — White Team's logic for updating `RevisableStrategy` mid-episode (e.g., after a PIVOT). Never touches `FrozenConstraints` — enforced at the type level, not just convention.

**`constraint_enforcer.py`** — The single enforcement point (this absorbs what v2 mistakenly split into two files). Key function: `check(action, contract: RoEContract) -> EnforcementResult` where `EnforcementResult` is `ALLOWED` or `BLOCKED(reason)`. On `BLOCKED`, writes to `audit/audit_log.py`.

---

## src/adapt/mitre/

**`attack_mapper.py`** — Takes a natural-language subtask description (e.g., "attempt credential extraction on DC01") and maps it to one or more MITRE ATT&CK technique IDs. Key function: `map_to_technique(subtask: str) -> list[AttackTechnique]`. Likely implemented as embedding similarity against technique descriptions loaded by `mitre_attack_loader.py`.

**`skill_space.py`** — Defines `S_cyber`, the structured space of techniques CUV scores against. Holds the filtered technique set from `mitre_attack_config.yaml` and exposes lookup by tactic/technique ID.

---

## src/adapt/routing/

**`cuv_calculator.py`** — Implements `CUV = (exploit_success_rate × stealth_multiplier) / (cost_per_token × execution_time)`. Key function: `compute_cuv(subtask, technique: AttackTechnique, candidate_model) -> float`. Calls `task_estimator.py` for the two inputs it can't observe directly (success rate, stealth).

**`task_estimator.py`** — Estimates exploit-success-rate and stealth-multiplier for a given technique. Two modes: (1) **warm**, querying `csim_store.py` for historical PASS rates on similar past subtasks; (2) **cold-start**, a fixed heuristic table keyed by ATT&CK tactic when no CSIM history exists yet. Be ready to explain this exact cold-start/warm split if asked — it's your answer to the "how do you get this pre-execution" question.

**`model_router.py`** — Given a CUV score, picks a tier from `model_registry.yaml` and returns the actual model handle. Key function: `route(subtask) -> ModelHandle`.

**`model_scheduler.py`** — Queues/locks GPU access so Red Team, Blue Team, and embedding calls don't try to load conflicting local models simultaneously. Key function: `acquire(model_handle) -> ContextManager` (use as a `with` block around inference calls).

**`model_clients/ollama_client.py`** — Thin wrapper around the Ollama HTTP API (`generate`, `chat`, tool-calling passthrough).

**`model_clients/hf_client.py`** — Wrapper around `transformers`/vLLM for any model pulled directly from Hugging Face rather than through Ollama.

---

## src/adapt/context/

**`context_manager.py`** — Builds the actual prompt context for a given agent call: system prompt + relevant history + current contract state + relevant tool schemas. Key function: `build_context(agent_role, episode_state) -> Context`.

**`context_window.py`** — Trims/summarizes older history when it would exceed the current model's context window (this matters more here than with API models, since your local tiers have materially smaller windows). Key function: `fit_to_window(context, max_tokens) -> Context`.

**`prompt_templates.py`** — Per-agent, per-tier prompt templates. Smaller local models generally need more explicit, structured prompting than a frontier model would — this file is where you compensate for that.

---

## src/adapt/agents/

**`base_agent.py`** — Shared ReAct-style loop (Thought → Action → Observation), used by both Red and Blue agent classes so the reasoning pattern isn't duplicated. Key method: `Agent.step(context) -> Action`, looped by the orchestrator until the agent emits a terminal action for the round.

### red_team/

**`recon.py`** — Scans the current sandbox target for open ports, services, and known entry points. Key function: `scan(target_host) -> ReconResult`.

**`graph_builder.py`** — Builds all four program-analysis representations from target source:
- `build_ast(source) -> AST` (Python `ast` module, or `tree-sitter` for other languages)
- `build_cfg(ast) -> CFG` (`networkx` graph)
- `build_dfg(ast) -> DFG`
- `build_pdg(cfg, dfg) -> PDG`

**`exploit_generator.py`** — Takes the graph bundle from `graph_builder.py` (not raw source) plus the mapped ATT&CK technique, proposes a candidate exploit. Key function: `generate_exploit(graphs, technique) -> ExploitAttempt`.

**`payload_mutator.py`** — Mutates a candidate exploit across attempts, seeded by `atomic_redteam_loader.py` playbooks so mutations stay realistic rather than arbitrary. Triggered specifically on a PIVOT outcome.

**`tools/port_scan_tool.py`**, **`payload_execute_tool.py`** — Callable functions the Red Team LLM invokes via tool-calling; thin wrappers that actually touch the sandbox.

**`tools/kerberoast_tool.py`**, **`asrep_roast_tool.py`**, **`rodc_dump_tool.py`** — AD-specific attack tools, modeled on the patterns in `splunk_ad_kerberos_loader.py`'s Event ID 4769/4104 data.

**`tools/tool_schema.py`** — JSON-schema descriptions of every Red Team tool, passed to the local model's function-calling interface.

### blue_team/

**`telemetry_ingest.py`** — Reads the live event stream from `sandbox/telemetry_producers/` (eBPF + Sysmon-Linux). Key function: `ingest_events() -> Iterator[TelemetryEvent]`.

**`patch_synthesizer.py`** — Given a detected breach + its graph representation, generates a code-level patch. Key function: `synthesize_patch(breach, graphs) -> Patch`.

**`yara_rule_generator.py`** — Generates a YARA detection rule from the same breach event, for future prevention (distinct output from the patch itself).

**`tools/telemetry_query_tool.py`**, **`patch_deploy_tool.py`**, **`tool_schema.py`** — mirrors the Red Team tool pattern.

---

## src/adapt/verification/

**`triage_gateway.py`** — The decision point. Key function: `triage(red_outcome, blue_outcome, contract) -> Verdict` where `Verdict` is `PASS`, `BLOCK`, or `PIVOT`. On `PASS`, calls `csim_store.commit()`. On `BLOCK`, calls `audit_log.record()` and reverts sandbox state via `container_manager.reset()`.

**`outcome_classifier.py`** — Determines, from raw agent actions and telemetry, whether Red actually succeeded and whether Blue actually succeeded — the inputs `triage_gateway.py` needs. This is where "did the exploit really work" gets decided, separate from the triage logic itself.

---

## src/adapt/memory/

**`csim_store.py`** — The "vaccine registry." Key function: `commit(exploit, patch)`, only ever called from a `PASS` verdict. Also `query_similar(subtask) -> list[HistoricalRecord]`, used by `task_estimator.py`.

**`embedding.py`** — Turns an exploit-patch pair (or a subtask description) into a vector, using a local embedding model (not an API).

**`vector_db_client.py`** — Thin wrapper around Chroma, running fully local — no external service dependency.

---

## src/adapt/sandbox/

**`container_manager.py`** — Spins up and tears down/resets the Docker container network. Key functions: `start()`, `reset()`.

**`network_isolator.py`** — Enforces the sealed-box network boundary — the actual firewall/namespace rules preventing sandbox traffic from reaching the host.

**`mininet_topology.py`** — Builds the Mininet network fabric the AD lab and Impacket traces run over. Key function: `build_topology(config: sandbox_topology.yaml) -> Network`.

**`targets/vulnerable_apps/`** — Seeded-vulnerability target applications (deliberately flawed web apps/services) for Red Team to attack outside the AD-specific scenarios.

**`targets/ad_lab_config.py`** — Defines the simulated Active Directory domain (domain controller, user accounts, Kerberos setup) that the AD-specific attack tools target.

**`telemetry_producers/ebpf_probes/`** — The actual eBPF programs attached inside sandbox containers, emitting kernel-level events.

**`telemetry_producers/sysmon_linux_config.py`** — Configuration for Microsoft's Sysmon-for-Linux, generating syscall-level events (execve, ptrace, etc.) that `telemetry_ingest.py` reads.

---

## src/adapt/schemas.py

Typed data models (Pydantic) for every cross-module object: `RoEContract`, `ExploitAttempt`, `TriageOutcome`, `CUVScore`, `AttackTechnique`, `TelemetryEvent`. Every other module imports from here rather than passing loosely-shaped dicts around — this is what makes "what does K_t look like in code" a concrete, answerable question.

---

## src/adapt/audit/audit_log.py

Appends a record every time `constraint_enforcer.py` returns `BLOCKED`: what was attempted, which constraint it violated, timestamp. Key function: `record(action, reason)`. This is the evidence behind your safety claim in the conclusion — without it, "the contract prevents unsafe actions" isn't verifiable after the fact.

---

## src/adapt/utils/

**`logger.py`** — Standard structured logging setup, used everywhere.

**`metrics.py`** — Tracks running counts: PASS/BLOCK/PIVOT rate, per-round model cost, cumulative cost vs. the baseline. Feeds `eval/cost_analysis.py`.

---

## baseline/

**`baseline_llm.py`** — A deliberately simple comparison system: one frontier-equivalent local model handling every subtask, no CUV routing, no tiering. Used to measure what routing actually saves.

**`baseline_scanner.py`** — Wraps a traditional (non-agentic) vulnerability scanner over the same sandbox targets, for the "does an agentic approach even help" comparison your objectives slide calls for.

**`cybench_adapter.py`**, **`nyu_ctf_adapter.py`** — Harnesses that run A.D.A.P.T. against the Cybench and NYU CTF Bench task sets respectively, so your results are comparable to published numbers rather than only internal ones.

---

## eval/

**`run_comparison.py`** — Runs the full system, `baseline_llm.py`, and `baseline_scanner.py` against the same sandbox targets and collects results side by side.

**`cost_analysis.py`** — Computes actual cost deltas from `metrics.py` output across the three conditions. **This is the file that produces your 60–80% number** — without running it, that figure in your conclusion is a target, not a result.

**`results_dashboard.py`** — Minimal output (HTML/plot) summarizing PASS/BLOCK/PIVOT rates and cost comparison, for demo purposes.

---

## tests/

Standard pytest files per module, plus:

**`test_graph_builder.py`** — Validates AST/CFG/DFG/PDG output against known sample code with a hand-verified expected graph.

**`test_attack_mapper.py`** — Validates subtask → ATT&CK technique mapping against a small labeled set.

**`conftest.py`** — Shared fixtures that mock local model calls, so the test suite runs in CI without needing a loaded GPU.

---

## scripts/

**`run_simulation.py`** — Entry point: builds the sandbox, runs `orchestrator.run_episode()` for N rounds.

**`run_baseline.py`** — Same, but against `baseline_llm.py`/`baseline_scanner.py` instead of the full system.

**`pull_local_models.sh`** — One-line setup: `ollama pull` for every model named in `model_registry.yaml`.

**`reset_sandbox.sh`** — Tears down and rebuilds the Docker/Mininet environment from scratch.
