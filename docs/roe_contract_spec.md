# RoE Contract Spec

## Shape of `K_t`

`K_t = (I, O_t, C_t, V_t)`, implemented as `adapt.schemas.RoEContract` with two
nested blocks:

| Symbol | Field | Block | Mutability |
|---|---|---|---|
| `I` | `intent` | `frozen_constraints` | Set once, at episode start |
| `C_t` | `prohibited_subnets`, `max_execution_time_s`, `absolute_rules` | `frozen_constraints` | Never mutated |
| `O_t` | `objective` | `revisable_strategy` | Updatable by White Team each round |
| `V_t` | `verification_criteria` | `revisable_strategy` | Updatable by White Team each round |

```yaml
frozen_constraints:
  intent: string
  prohibited_subnets: list
  max_execution_time_s: int
  absolute_rules: list

revisable_strategy:
  objective: string
  verification_criteria: list
```

(See `config/roe_contract_schema.yaml` for the schema and
`src/adapt/schemas.py` for the Pydantic models.)

## Why the split matters

Splitting the contract into a frozen tier and a revisable tier at the type
level -- rather than by convention -- means `contract.contract_writer` simply
has no way to touch `frozen_constraints`; there's nothing to enforce by
review. Every agent action passes through the single enforcement point,
`contract.constraint_enforcer.check(action, contract)`, which returns
`EnforcementResult.ok()` or `EnforcementResult.blocked(reason)`. A `BLOCKED`
result is always written to `audit.audit_log.record`, which is what makes the
project's safety claim ("the contract prevents unsafe actions") verifiable
after the fact rather than just asserted.

## Round lifecycle

1. Episode starts: White Team sets `frozen_constraints` once.
2. Each round: White Team may update `revisable_strategy` (e.g. after a
   `PIVOT`), via `contract.contract_writer.update_strategy`.
3. Every agent action is checked against the *current* contract before
   execution.
4. `verification.triage_gateway.triage` uses `V_t` (verification_criteria) to
   decide `PASS` / `BLOCK` / `PIVOT` for the round.
