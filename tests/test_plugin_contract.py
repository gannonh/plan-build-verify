from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOSTS = ("cursor", "claude", "codex")
EXPECTED_SKILLS = ("plan", "build", "review", "verify", "triage")
REQUIRED_STATES = (
    "Backlog",
    "Todo",
    "In Progress",
    "Agent Review",
    "Human Review",
    "Merging",
    "Done",
    "Canceled",
    "Duplicate",
)
REMOVED_PATHS = (
    "src/skills/plan/scripts/ensure_labels.sh",
    "src/skills/plan/scripts/migrate_specs.sh",
    "src/skills/plan/scripts/rewrite_spec_links.py",
    "src/skills/plan/references/migration.md",
    "src/skills/ship/SKILL.md",
    "tests/test_migrate_specs.py",
    "tests/conftest.py",
)
FORBIDDEN_SNIPPETS = (
    "gh issue create",
    "gh sub-issue",
    "gh issue edit",
    "gh issue close",
    "status:approved",
    "kind:spec",
    "ensure_labels.sh",
    "migrate_specs.sh",
    "rewrite_spec_links.py",
)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def load_check():
    path = ROOT / "scripts" / "check.py"
    spec = importlib.util.spec_from_file_location("pbv_check", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["pbv_check"] = module
    spec.loader.exec_module(module)
    return module


def skill_text(host: str, skill: str, rel: str) -> str:
    return (ROOT / "plugins" / host / "skills" / skill / rel).read_text(encoding="utf-8")


def iter_source_markdown() -> list[Path]:
    roots = [
        ROOT / "src",
        ROOT / "docs",
        ROOT / ".cursor" / "skills" / "verify-plan-build-verify",
        ROOT / "README.md",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        files.extend(path for path in root.rglob("*") if path.suffix in {".md", ".json", ".mjs", ".py"} and path.is_file())
    return files


def test_generated_trees_satisfy_host_contract() -> None:
    check = load_check()
    errors = check.collect_errors(ROOT, require_git_clean=False)
    assert errors == [], "\n".join(errors)


def test_each_host_distributes_review_skill_at_version_0_2_0() -> None:
    for host in HOSTS:
        tree = ROOT / "plugins" / host
        observed = sorted(p.name for p in (tree / "skills").iterdir() if p.is_dir())
        assert observed == sorted(EXPECTED_SKILLS), f"{host} skills {observed}"
        assert not (tree / "skills" / "ship").exists()
        frontmatter = (tree / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
        assert frontmatter.startswith("---\nname: review\n")
        manifest = json.loads((tree / f".{host}-plugin" / "plugin.json").read_text(encoding="utf-8"))
        assert manifest["version"] == "0.2.0"


def test_marketplace_catalogs_are_version_0_2_0() -> None:
    claude = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert claude["plugins"][0]["version"] == "0.2.0"
    cursor = json.loads((ROOT / "plugins" / "cursor" / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert cursor["version"] == "0.2.0"


def test_obsolete_migrate_and_ship_paths_are_gone() -> None:
    for rel in REMOVED_PATHS:
        assert not (ROOT / rel).exists(), rel
    for host in HOSTS:
        tree = ROOT / "plugins" / host
        assert not (tree / "skills" / "ship").exists()
        assert not (tree / "skills" / "plan" / "scripts").exists()
        assert not (tree / "skills" / "plan" / "references" / "migration.md").exists()
        assert not (tree / "skills" / "verify" / "scripts" / "user-acceptance").exists()
        assert not (tree / "skills" / "verify" / "references" / "user-acceptance").exists()


def test_shared_conventions_encode_linear_lifecycle_gates() -> None:
    text = (ROOT / "src" / "shared" / "conventions.md").read_text(encoding="utf-8")
    assert "The Linear issue and any parent epic are the spec." in text
    assert "GitHub Issues are inbound context only." in text
    assert "Do not include a Status section." in text
    for state in REQUIRED_STATES:
        assert state in text, state
    for field in (
        '"title"',
        '"team"',
        '"project"',
        '"state"',
        '"id"',
        '"description"',
        '"parentId"',
        '"blockedBy"',
        '"blocks"',
        '"relatedTo"',
        '"labels"',
        '"links"',
        '"includeRelations"',
        '"issueId"',
        '"body"',
        '"query"',
        '"includeArchived"',
        '"cursor"',
    ):
        assert field in text, field
    assert "save_issue({" in text
    assert "get_issue({" in text
    assert "save_comment({" in text
    assert "list_issue_statuses({" in text
    assert "gitBranchName" in text
    assert "docs/development-lifecycle.md" in text
    assert "## Status" not in text.split("## Spec issue body template", 1)[1]


def test_build_owns_pre_merge_acceptance_assets() -> None:
    build_scripts = ROOT / "src" / "skills" / "build" / "scripts" / "user-acceptance"
    assert (build_scripts / "verify-evidence.mjs").is_file()
    assert (ROOT / "src" / "skills" / "build" / "references" / "user-acceptance" / "workflow.md").is_file()
    assert (ROOT / "src" / "skills" / "build" / "references" / "user-acceptance" / "evals" / "evals.json").is_file()
    assert not (ROOT / "src" / "skills" / "verify" / "scripts").exists()
    assert not (ROOT / "src" / "skills" / "verify" / "references" / "user-acceptance").exists()
    verify = (ROOT / "src" / "skills" / "verify" / "references" / "verify.md").read_text(encoding="utf-8")
    assert "../build/references/user-acceptance/workflow.md" in verify or "<plugin-root>/skills/build/scripts/user-acceptance/" in verify
    assert "gh pr create" not in verify
    build = (ROOT / "src" / "skills" / "build" / "references" / "build.md").read_text(encoding="utf-8")
    assert "gh pr create --draft" in build
    assert "verify-plan-build-verify" in build
    assert "Agent Review" in build


def test_review_skill_preserves_agent_reviews_and_lifecycle_gates() -> None:
    text = (ROOT / "src" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    assert "npx agent-reviews --expanded --json" in text
    assert "npx agent-reviews --reply" in text
    assert "--resolve" in text
    assert "Thread resolved" in text
    assert "Thread already resolved" in text
    assert "gh pr comment" in text
    assert "follow-up replies" in text
    assert "filters are not closure evidence" in text
    assert "Human Review" in text
    assert "Merging" in text
    assert "## PR closed without merge" in text
    assert "gh pr merge" in text
    assert "Do not paginate review comments with raw `gh`." in text


def test_plan_ends_at_human_todo_approval() -> None:
    text = (ROOT / "src" / "skills" / "plan" / "references" / "plan.md").read_text(encoding="utf-8")
    assert '"state": "Backlog"' in text
    assert "Plan does not write Todo." in text
    assert "save_issue({" in text
    assert "gh issue create" not in text


def test_verify_starts_after_done_and_keeps_original_done() -> None:
    text = (ROOT / "src" / "skills" / "verify" / "references" / "verify.md").read_text(encoding="utf-8")
    assert "Verify starts after Done." in text
    assert "Leave the original issue in Done." in text
    assert '"state": "Backlog"' in text
    assert "Auto-close is not evidence" in text
    assert "gh pr list --search" in text


def test_development_lifecycle_records_kata_sh_policy() -> None:
    text = (ROOT / "docs" / "development-lifecycle.md").read_text(encoding="utf-8")
    assert "Gannon Hall" in text
    assert "2026-09-04" in text
    assert "Draft PR open" in text
    assert "Move issue to In Progress" in text
    assert "Move issue to Agent Review" in text
    assert "Move issue to Done" in text
    assert "None configured." in text
    assert "waived the live scratch" in text


def test_relation_removal_uses_explicit_mcp_fields() -> None:
    conventions = (ROOT / "src/shared/conventions.md").read_text()
    for field in ("removeBlockedBy", "removeBlocks", "removeRelatedTo"):
        assert field in conventions
    for rel in ("src/skills/build/references/build.md", "src/skills/triage/references/triage.md"):
        text = (ROOT / rel).read_text()
        assert "removeBlockedBy" in text
        assert "saving remaining" not in text
        assert '"blockedBy": []' not in text


def test_source_instructions_drop_github_spec_and_migrate_commands() -> None:
    for path in iter_source_markdown():
        rel = path.relative_to(ROOT)
        if rel.parts[:3] == ("src", "skills", "triage"):
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in FORBIDDEN_SNIPPETS:
            assert snippet not in text, f"{rel}: {snippet}"


def test_triage_keeps_inbound_github_issue_commands_only() -> None:
    text = (ROOT / "src" / "skills" / "triage" / "references" / "triage.md").read_text(encoding="utf-8")
    assert "gh issue list" in text
    assert "gh issue view" in text
    assert "gh issue comment" in text
    assert "gh issue create" not in text
    assert "gh sub-issue" not in text
    assert "Never implement from the GitHub Issue." in text


def test_agents_and_commands_match_new_timing() -> None:
    build_agent = (ROOT / "src" / "agents" / "cursor" / "build-agent.md").read_text(encoding="utf-8")
    verify_agent = (ROOT / "src" / "agents" / "cursor" / "verify-agent.md").read_text(encoding="utf-8")
    assert "Open a draft PR while the issue is In Progress." in build_agent
    assert "Do not continue into Review or Verify." in build_agent
    assert "merged state" in verify_agent
    assert not (ROOT / "src" / "commands" / "review.md").exists()
    assert not (ROOT / "src" / "commands" / "triage.md").exists()
    assert not (ROOT / "src" / "agents" / "cursor" / "review-agent.md").exists()


def test_referenced_markdown_targets_exist() -> None:
    missing: list[str] = []
    roots = [ROOT / "src", ROOT / "docs", ROOT / ".cursor" / "skills" / "verify-plan-build-verify"]
    for root in roots:
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for match in MD_LINK.finditer(text):
                target = match.group(1).split("#", 1)[0].split(" ", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert missing == [], "\n".join(missing)


def test_generated_hosts_share_review_and_build_acceptance_ownership() -> None:
    for host in HOSTS:
        tree = ROOT / "plugins" / host
        assert (tree / "skills" / "build" / "scripts" / "user-acceptance" / "verify-evidence.mjs").is_file()
        assert (tree / "skills" / "review" / "SKILL.md").is_file()
        assert not (tree / "skills" / "verify" / "scripts" / "user-acceptance").exists()
        conventions = skill_text(host, "plan", "references/conventions.md")
        assert conventions == skill_text(host, "review", "references/conventions.md")
        assert "The Linear issue and any parent epic are the spec." in conventions
