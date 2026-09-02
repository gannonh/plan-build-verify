from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_check():
    path = ROOT / "scripts" / "check.py"
    spec = importlib.util.spec_from_file_location("pbv_check", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["pbv_check"] = module
    spec.loader.exec_module(module)
    return module


def test_generated_trees_satisfy_host_contract() -> None:
    check = load_check()
    errors = check.collect_errors(ROOT, require_git_clean=False)
    assert errors == [], "\n".join(errors)
