# Linear lifecycle verification

Scope: KAT-3233, plugin version 0.2.0. Candidate: `4e19c85f020656d2119da3e374dadc0562931f5d`. Date: 2026-09-04.

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
38 passed in 1.62s

claude plugin validate ./plugins/claude --strict
Validation passed
```

Python 3.11.11 ran in a temporary environment with `requirements-dev.txt`. The five skill entrypoints also passed the skill-authoring validator. Its PyYAML dependency was installed only in that temporary environment.

## Installed candidates

Run: `20260904T141558-56494`, under `uat-evidence/verify-plan-build-verify/`.

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

The gitignored `uat-evidence/linear-lifecycle-pr-fixes/` directory holds the evidence manifest, report, and captured command logs with exit codes. The installed-candidate run holds `run.json`, launch/doctor logs, feature results, listings, manifests, and copied command files. Earlier candidate evidence remains in its original directories.

The independent spec review passed with no blocking findings. Its label-preservation and tool-discovery nits were addressed before the candidate commit. The code-comment audit found no comments to remove.

The Fable code-quality and decision-trail review stopped with HTTP 429 at the monthly usage-credit limit. The user approved GPT-5.6 Sol for the remaining review, recorded in Linear comment `f6c214d4-5ecd-4bfd-b476-b1a0c91df202`.

Sol found two issues: the acceptance evals still expected conversational sign-off, and Verify gave conflicting instructions for a Done issue with no merged PR. Both were corrected with regression coverage. Sol's focused recheck returned `Ready: Yes` for `f4ad442`, with no remaining findings. The evidence validator also passed on that candidate.

The GitHub Codex bot then identified implicit PR selection in Review and an incomplete no-PR exception in Build. Commit `4e19c85` binds Review commands to one repository and PR, checks the checkout's head before edits, and requires draft PR creation before Build continues. Two added contract tests reproduced the failures. Sol's focused recheck returned `Ready: Yes`, with no remaining issue in this delta. The four required commands, four isolated drives, copy equality checks, and evidence validator passed again.

## Regression evidence

The tests below failed before their corresponding corrections. These excerpts preserve the observed failure conditions from the task transcript:

```text
test_relation_removal_uses_explicit_mcp_fields
AssertionError: assert 'removeBlockedBy' in conventions

test_report_uses_linear_workflow_without_extra_approval_gate
AssertionError: assert 'Linear workflow states' in report
Observed report ended with: Recommendation: Pending user sign-off

test_verify_starts_after_done_and_keeps_original_done
AssertionError: 'No merged PR can be identified' is contained in the stop-and-ask section

test_acceptance_evals_use_linear_approval_gate
AssertionError: 0
'sign-off' is contained in the first eval's expected output

test_review_commands_keep_the_resolved_pr_target
AssertionError: view
The gh pr view example lacked the resolved PR number and repository.

test_build_requires_the_draft_pr_before_ready
AssertionError: 'merges without PRs' is contained in the Build workflow
```

After correction, all 38 tests passed. The report regression executes the public Node command and validates the generated evidence. The other checks protect the instruction and fixture contracts. Sol's trail audit matched the earlier recorded red-green decisions to the transcript.

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
