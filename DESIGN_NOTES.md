# Design Notes (Non-Normative)

This document is informational and does not define contract semantics.

## Determinism Requirements
- All output must be canonicalized (stable key order, stable list ordering)
- No timestamps
- No environment-dependent paths in outputs (only relative paths)

## Evaluation Inputs (Read-only)
- Repo filesystem contents
- Known dependency files (examples):
  - Python: requirements.txt, requirements.lock, poetry.lock, pyproject.toml
  - Node: package-lock.json, pnpm-lock.yaml, yarn.lock, package.json
  - Others as needed (explicitly listed; no guessing)

## Fail-Closed Policy
- If the guardian cannot parse a dependency file deterministically, fail_closed = true
- Missing expected artifacts where policy requires them => ok = false

## Output Philosophy
- Emit only evidence necessary for deterministic gating.
- Avoid verbose reporting; focus on stable, minimal facts.
