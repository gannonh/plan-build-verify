# Linear lifecycle verification

Scope: KAT-3233, plugin version 0.2.0. Candidate: `26a9aa6599d24c9bb29ddd7335387a9af70b889f`. Date: 2026-09-04.

The maintainer waived the live scratch Linear/GitHub workflow demonstration. No scratch team, repo, seeded review thread, or manual test transition was required. This report covers source contracts and isolated installed copies. It does not prove live workflow automation.

## Automated results

All commands exited 0 on the committed candidate:

```text
python3 scripts/build.py
wrote plugins/cursor, plugins/claude, plugins/codex
wrote .cursor-plugin/marketplace.json
wrote .claude-plugin/marketplace.json
wrote .agents/plugins/marketplace.json

python3 scripts/check.py
plugin trees match src/ and host layout rules

python3 -m pytest
34 passed in 1.68s

claude plugin validate ./plugins/claude --strict
Validation passed
```

Python 3.11.11 ran in a temporary environment with `requirements-dev.txt`. The five skill entrypoints also passed the skill-authoring validator. Its PyYAML dependency was installed only in that temporary environment.

## Installed candidates

Run: `20260904T133916-61651`, under `uat-evidence/verify-plan-build-verify/`.

Launch, doctor, and all four drives passed: `cursor-local-install`, `claude-plugin`, `codex-plugin`, and `documented-build`. Strict Claude validation passed on the isolated copy. A second read with `diff -qr` found no differences between each generated tree and its installed copy.

Observed on Cursor and Claude:

```text
skills build, plan, review, triage, verify
agents build-agent.md, plan-agent.md, verify-agent.md
commands build.md, plan.md, verify.md
```

Observed on Codex:

```text
skills build, plan, review, triage, verify
agents (absent)
commands (absent)
```

Each copy contained only its host's manifest directory. All manifests reported version 0.2.0.

Live Cursor and Claude plugin UI: `verified-unreachable`. The isolated run had no dedicated host UI session. Installed-copy inventories do not prove UI rendering or discovery.

## Evidence

The gitignored `uat-evidence/linear-lifecycle-candidate/` directory holds the evidence manifest, report, and captured command logs with exit codes. The installed-candidate run holds `run.json`, launch/doctor logs, feature results, listings, manifests, and copied command files. `verify-evidence.mjs` reported `Evidence OK`.

The independent spec review passed with no blocking findings. Its label-preservation and tool-discovery nits were addressed before the candidate commit. The code-comment audit found no comments to remove.

The final Fable code-quality and decision-trail review stopped with HTTP 429 at the monthly usage-credit limit. It produced no completed review. No fallback model was used and no PR was opened. A remaining report-wording cleanup must replace the old accept/reject prompt with the Linear workflow handoff, then rerun affected checks before PR creation.

## Repeat the checks

From a committed checkout with Python test requirements and Claude Code installed:

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m pytest
claude plugin validate ./plugins/claude --strict
.cursor/skills/verify-plan-build-verify/scripts/control-pbv launch
```

Use the printed run ID for each subsequent command:

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> doctor
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> drive cursor-local-install
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> drive claude-plugin
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> drive codex-plugin
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> drive documented-build
.cursor/skills/verify-plan-build-verify/scripts/control-pbv --run-id <run-id> cleanup
```

Doctor prints `ready`; every drive prints `proved`. Cleanup removes only the run's temporary `home/` and retains evidence. No live host plugin directory is modified.
