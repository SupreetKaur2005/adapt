# A.D.A.P.T.

**A.D.A.P.T.** is a fully local, LLM-routed red-team / blue-team cyber-range simulator.
A White Team agent maintains a Rules-of-Engagement contract (`K_t`); a Red Team agent
attacks seeded, sandboxed targets (including a simulated AD/Kerberos domain) while a
Blue Team agent detects and patches; every action is routed across local model tiers
(via Ollama) by a cost/stealth-aware router (TOPAZ) and scored against a MITRE ATT&CK
skill space. Outcomes are triaged as `PASS` / `BLOCK` / `PIVOT`, with every `BLOCK`
written to an audit log and every `PASS` committed to a vector-backed episodic memory
(CSIM) that improves future routing decisions.

No cloud APIs are used anywhere in the pipeline -- models, embeddings, and the vector
store all run locally.

## Architecture at a glance

- **`src/adapt/orchestrator.py`** -- the episode loop: round number, whose turn, active
  contract, history.
- **`contract/`** -- the RoE contract (`FrozenConstraints` + `RevisableStrategy`) and its
  single enforcement point.
- **`mitre/`** -- maps subtasks onto MITRE ATT&CK techniques (`S_cyber`).
- **`routing/`** -- TOPAZ: computes CUV (cost/success/stealth) and routes each subtask to
  a local model tier.
- **`agents/red_team/`**, **`agents/blue_team/`** -- the two adversarial agents and their
  sandbox tools.
- **`verification/`** -- the `PASS`/`BLOCK`/`PIVOT` triage gateway.
- **`memory/`** -- CSIM, the episodic "vaccine registry" (local Chroma vector store).
- **`sandbox/`** -- Mininet network fabric, AD lab, vulnerable targets, telemetry
  producers (eBPF + Sysmon-Linux).
- **`baseline/`**, **`eval/`** -- monolithic-LLM and traditional-scanner baselines, plus
  the cost-delta analysis they're compared against.

See [`ADAPT_File_Details.md`](ADAPT_File_Details.md) for the complete file-by-file spec,
and [`docs/architecture.md`](docs/architecture.md) / [`docs/roe_contract_spec.md`](docs/roe_contract_spec.md)
for narrative detail.

## Quickstart

```bash
# 1. Install the package (editable) + dev deps
pip install -e ".[dev]"

# 2. Pull the local models this project routes across
./scripts/pull_local_models.sh

# 3. Bring up the sandbox (Ollama + sandbox + telemetry containers)
docker compose -f docker/docker-compose.yml up -d

# 4. Run a simulation episode
python scripts/run_simulation.py --rounds 10
```

Run the test suite (mocks all local-model calls, so no GPU is required) with:

```bash
pytest
```
