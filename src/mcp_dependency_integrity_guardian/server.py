from __future__ import annotations

import json
import os
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Check:
    id: str
    kind: str  # "file_present" | "requirements_pins"
    path: str


CHECKS: List[Check] = [
    Check(id="python_requirements_present", kind="file_present", path="requirements.txt"),
    Check(id="python_poetry_lock_present", kind="file_present", path="poetry.lock"),
    Check(id="node_package_json_present", kind="file_present", path="package.json"),
    Check(id="node_package_lock_present", kind="file_present", path="package-lock.json"),
    Check(id="node_pnpm_lock_present", kind="file_present", path="pnpm-lock.yaml"),
    Check(id="node_yarn_lock_present", kind="file_present", path="yarn.lock"),
    Check(id="python_requirements_pins", kind="requirements_pins", path="requirements.txt"),
]


def _abspath(repo_path: str, rel: str) -> str:
    return os.path.join(repo_path, rel)


def _is_file(repo_path: str, rel: str) -> bool:
    return os.path.isfile(_abspath(repo_path, rel))


def _read_text(repo_path: str, rel: str) -> str:
    with open(_abspath(repo_path, rel), "r", encoding="utf-8") as f:
        return f.read()


def _parse_requirements_unpinned(lines: List[str]) -> List[str]:
    offenders: List[str] = []
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith(("-r ", "--requirement ", "-c ", "--constraint ")):
            continue
        if s.startswith(("--index-url", "--extra-index-url", "--find-links", "--trusted-host")):
            continue
        if s.startswith(("-e ", "--editable ")):
            offenders.append(s)
            continue
        if "@" in s:
            continue
        if "==" in s:
            continue
        offenders.append(s)
    offenders.sort()
    return offenders


def _requirements_check(repo_path: str, rel: str) -> Dict[str, Any]:
    if not _is_file(repo_path, rel):
        return {
            "check_id": "python_requirements_pins",
            "path": rel,
            "kind": "requirements_pins",
            "present": False,
            "ok": True,
            "unpinned": [],
            "note": "requirements.txt not present; pinning check skipped",
        }

    txt = _read_text(repo_path, rel)
    lines = txt.splitlines()
    offenders = _parse_requirements_unpinned(lines)
    ok = len(offenders) == 0
    return {
        "check_id": "python_requirements_pins",
        "path": rel,
        "kind": "requirements_pins",
        "present": True,
        "ok": ok,
        "unpinned": offenders,
    }


def evaluate(repo_path: str) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    try:
        present_map = {c.id: _is_file(repo_path, c.path) for c in CHECKS if c.kind == "file_present"}

        results.extend(
            [
                {
                    "check_id": c.id,
                    "path": c.path,
                    "kind": c.kind,
                    "present": present_map.get(c.id, False),
                }
                for c in CHECKS
                if c.kind == "file_present"
            ]
        )

        results.append(_requirements_check(repo_path, "requirements.txt"))

        python_lock_ok = present_map.get("python_requirements_present", False) or present_map.get(
            "python_poetry_lock_present", False
        )
        node_lock_ok = (not present_map.get("node_package_json_present", False)) or (
            present_map.get("node_package_lock_present", False)
            or present_map.get("node_pnpm_lock_present", False)
            or present_map.get("node_yarn_lock_present", False)
        )

        req_pins_ok = True
        for r in results:
            if r.get("check_id") == "python_requirements_pins":
                req_pins_ok = bool(r.get("ok", False))

        ok = bool(python_lock_ok and node_lock_ok and req_pins_ok)

        return {
            "guardian": "mcp-dependency-integrity-guardian:v1",
            "ok": ok,
            "fail_closed": False,
            "checks": results,
        }

    except Exception:
        tb = traceback.format_exc().splitlines()
        return {
            "guardian": "mcp-dependency-integrity-guardian:v1",
            "ok": False,
            "fail_closed": True,
            "error": {
                "type": "guardian_internal_error",
                "message": "guardian threw exception during evaluation",
                "traceback_tail": tb[-20:],
            },
            "checks": results,
        }


def main(argv: List[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    repo_path = argv[0] if len(argv) >= 1 else "."
    out = evaluate(repo_path)
    sys.stdout.write(canonical_json(out) + "\n")


if __name__ == "__main__":
    main()
