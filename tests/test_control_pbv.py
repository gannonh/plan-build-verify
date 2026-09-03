from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[1]
CONTROL_PBV = REPO / ".cursor/skills/verify-plan-build-verify/scripts/control-pbv"
EVIDENCE_REL = Path("uat-evidence") / "verify-plan-build-verify"


@pytest.fixture()
def control_pbv():
    loader = SourceFileLoader("control_pbv", str(CONTROL_PBV))
    spec = importlib.util.spec_from_loader("control_pbv", loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["control_pbv"] = module
    loader.exec_module(module)
    return module


def run_control(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, str(CONTROL_PBV), *args],
        cwd=REPO,
        env=merged,
        capture_output=True,
        text=True,
    )


def write_run_json(run_dir: Path, *, version: str = "0.1.0", **overrides: str) -> None:
    payload = {
        "run_id": run_dir.name,
        "repo": str(REPO),
        "root": str(run_dir),
        "home": str(run_dir / "home"),
        "evidence": str(run_dir / "evidence"),
        "cursor_install": str(run_dir / "home" / ".cursor" / "plugins" / "local" / "plan-build-verify"),
        "claude_install": str(
            run_dir
            / "home"
            / ".claude"
            / "plugins"
            / "cache"
            / "plan-build-verify"
            / "plan-build-verify"
            / version
        ),
        "codex_install": str(
            run_dir
            / "home"
            / ".codex"
            / "plugins"
            / "cache"
            / "plan-build-verify"
            / "plan-build-verify"
            / version
        ),
        "version": version,
    }
    payload.update(overrides)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


@pytest.fixture()
def evidence_base(tmp_path: Path, control_pbv, monkeypatch: pytest.MonkeyPatch) -> Path:
    base = tmp_path / EVIDENCE_REL
    base.mkdir(parents=True)
    monkeypatch.setattr(control_pbv, "repo_root", lambda: REPO)
    monkeypatch.setattr(control_pbv, "evidence_base", lambda repo: base)
    monkeypatch.setattr(control_pbv, "assert_not_operator_plugin", lambda path: None)
    return base


def test_run_dir_from_id_rejects_escape(control_pbv, evidence_base: Path) -> None:
    outside = evidence_base.parent / "outside-run"
    outside.mkdir()
    write_run_json(outside)

    with pytest.raises(SystemExit, match="must not escape"):
        control_pbv.run_dir_from_id(evidence_base, "..")

    with pytest.raises(SystemExit, match="must not be absolute"):
        control_pbv.run_dir_from_id(evidence_base, str(outside))

    with pytest.raises(SystemExit, match="single directory name"):
        control_pbv.run_dir_from_id(evidence_base, "nested/run")


def test_load_run_binds_paths_to_selected_directory(control_pbv, evidence_base: Path) -> None:
    run_dir = evidence_base / "bound-run"
    decoy_home = evidence_base.parent / "decoy-home"
    decoy_home.mkdir()
    write_run_json(
        run_dir,
        root=str(evidence_base.parent),
        home=str(decoy_home),
        evidence=str(evidence_base.parent / "decoy-evidence"),
        cursor_install=str(decoy_home / "cursor"),
        claude_install=str(decoy_home / "claude"),
        codex_install=str(decoy_home / "codex"),
    )

    run = control_pbv.load_run(run_dir)

    assert run.root_path == run_dir.resolve()
    assert run.home_path == (run_dir / "home").resolve()
    assert run.evidence_path == (run_dir / "evidence").resolve()
    assert run.cursor_install == str((run_dir / "home" / ".cursor" / "plugins" / "local" / "plan-build-verify").resolve())
    assert run.claude_install.endswith("plan-build-verify/0.1.0")
    assert run.codex_install.endswith("plan-build-verify/0.1.0")


def test_cleanup_only_removes_bound_home(control_pbv, evidence_base: Path) -> None:
    run_dir = evidence_base / "cleanup-run"
    decoy_home = evidence_base.parent / "decoy-home"
    decoy_home.mkdir()
    (decoy_home / "marker").write_text("keep", encoding="utf-8")
    write_run_json(run_dir, home=str(decoy_home))

    run = control_pbv.load_run(run_dir)
    bound_home = run_dir / "home"
    bound_home.mkdir()
    (bound_home / "staged").write_text("gone", encoding="utf-8")

    assert control_pbv.cmd_cleanup(run) == 0
    assert not bound_home.exists()
    assert decoy_home.is_dir()
    assert (decoy_home / "marker").read_text(encoding="utf-8") == "keep"


def test_documented_build_fails_when_staged_installs_are_missing(control_pbv, evidence_base: Path) -> None:
    run_dir = evidence_base / "doc-build-run"
    evidence = run_dir / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "launch.log").write_text(
        "wrote plugins/cursor, plugins/claude, plugins/codex\n"
        "wrote .cursor-plugin/marketplace.json\n"
        "wrote .claude-plugin/marketplace.json\n"
        "wrote .agents/plugins/marketplace.json\n",
        encoding="utf-8",
    )
    write_run_json(run_dir)
    run = control_pbv.load_run(run_dir)

    dest = evidence / "documented-build"
    dest.mkdir()
    errors = control_pbv.drive_documented_build(run, dest)

    assert any("missing run home" in error for error in errors)
    assert any("missing cursor install" in error for error in errors)
    assert any("missing claude install" in error for error in errors)
    assert any("missing codex install" in error for error in errors)


def test_drive_claude_validates_repository_tree_and_isolated_copy(control_pbv, tmp_path: Path) -> None:
    install = tmp_path / "isolated-claude"
    install.mkdir()
    dest = tmp_path / "evidence"
    dest.mkdir()
    run = control_pbv.Run(
        run_id="run",
        repo=str(REPO),
        root=str(tmp_path),
        home=str(tmp_path / "home"),
        evidence=str(dest),
        cursor_install=str(tmp_path / "home" / "cursor"),
        claude_install=str(install),
        codex_install=str(tmp_path / "home" / "codex"),
        version="0.1.0",
    )
    calls: list[list[str]] = []

    def fake_capture(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="ok\n", stderr="")

    with (
        patch.object(control_pbv.shutil, "which", return_value="/usr/bin/claude"),
        patch.object(control_pbv, "capture", side_effect=fake_capture),
        patch.object(control_pbv, "write_listing"),
        patch.object(control_pbv, "require_skills", return_value=[]),
        patch.object(control_pbv, "require_agents", return_value=[]),
        patch.object(control_pbv, "require_command_descriptions", return_value=[]),
    ):
        errors = control_pbv.drive_claude(run, dest)

    assert errors == []
    assert len(calls) == 2
    assert calls[0][3] == str(REPO / "plugins" / "claude")
    assert calls[1][3] == str(install)
    assert (dest / "validate-repo.log").is_file()
    assert (dest / "validate.log").is_file()
    assert "./plugins/claude" in (dest / "validate-repo.log").read_text(encoding="utf-8")


def test_documented_build_integration_fails_after_cleanup() -> None:
    launch = run_control("launch")
    assert launch.returncode == 0, launch.stderr
    run_id = launch.stdout.splitlines()[0].strip()

    cleanup = run_control("--run-id", run_id, "cleanup")
    assert cleanup.returncode == 0, cleanup.stderr

    drive = run_control("--run-id", run_id, "drive", "documented-build")
    assert drive.returncode != 0
    assert "missing run home" in drive.stderr or "missing cursor install" in drive.stderr

    shutil.rmtree(REPO / EVIDENCE_REL / run_id, ignore_errors=True)
