# mcp-dependency-integrity-guardian

A minimal deterministic, read-only, fail-closed guardian that enforces basic dependency integrity rules.

Scope (V1, frozen intent):
- Detect presence of dependency lock/pin artifacts (language-appropriate)
- Detect unpinned dependency declarations where applicable
- No network calls
- No mutation
- Deterministic output

Non-goals:
- No vulnerability/CVE scanning
- No dependency resolution
- No registry lookups
- No "best practice" suggestions beyond pass/fail evidence

This guardian is designed to compose under deterministic multi-guardian governance.
