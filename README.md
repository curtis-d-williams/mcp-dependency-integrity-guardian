# mcp-dependency-integrity-guardian

A minimal deterministic, read-only guardian that enforces basic dependency integrity rules (lockfiles + pinning checks).

## Scope (V1)

- Detect presence of dependency lock/pin artifacts (language-appropriate)
- Detect unpinned dependency declarations where applicable
- No network calls
- No mutation
- Deterministic output

## Non-goals

- No vulnerability/CVE scanning
- No dependency resolution
- No registry lookups
- No "best practice" suggestions beyond pass/fail evidence

This guardian is designed to compose under deterministic multi-guardian governance.

## V1 contract freeze (immutable under v0.x)

**No schema expansion, no new fields, no semantic drift, no nondeterminism.**

Output is canonical JSON (sorted keys, compact separators, UTF-8) with the following top-level fields:

- `guardian` (string): fixed identifier `mcp-dependency-integrity-guardian:v1`
- `ok` (bool): policy result for this guardian
- `fail_closed` (bool): execution fail-closed signal
  - `true` only on internal guardian exception
  - `false` on normal execution (including policy failures)
- `checks` (array[object]): ordered list of check result objects (deterministic order)
- Optional `error` (object): present only when `fail_closed` is `true`

If any change is required to:
- output structure
- field meanings
- determinism guarantees

→ designate **V2** and include migration notes (no silent changes).

## Deterministic example output (V1)

Below is a real canonical output captured by running the guardian against this repository:

```json
{"checks":[{"check_id":"python_requirements_present","kind":"file_present","path":"requirements.txt","present":false},{"check_id":"python_poetry_lock_present","kind":"file_present","path":"poetry.lock","present":false},{"check_id":"node_package_json_present","kind":"file_present","path":"package.json","present":false},{"check_id":"node_package_lock_present","kind":"file_present","path":"package-lock.json","present":false},{"check_id":"node_pnpm_lock_present","kind":"file_present","path":"pnpm-lock.yaml","present":false},{"check_id":"node_yarn_lock_present","kind":"file_present","path":"yarn.lock","present":false},{"check_id":"python_requirements_pins","kind":"requirements_pins","note":"requirements.txt not present; pinning check skipped","ok":true,"path":"requirements.txt","present":false,"unpinned":[]}],"fail_closed":false,"guardian":"mcp-dependency-integrity-guardian:v1","ok":false}

```

## Run locally

```bash
python3 -m pip install -e .
mcp-dependency-integrity-guardian .
```
