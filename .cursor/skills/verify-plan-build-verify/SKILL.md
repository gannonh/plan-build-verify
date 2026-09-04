---
name: verify-plan-build-verify
description: >-
  Drive and prove plan-build-verify plugin trees with an isolated Cursor local-plugin
  copy, Claude plugin validate, and Codex layout checks. Use when verifying this
  plugin, proving README install paths, running /verify-plan-build-verify, or checking
  Cursor, Claude, or Codex install artifacts without touching the operator's live
  plugin directories.
---

# Verify plan-build-verify

The user-facing product is the generated plugin trees under `plugins/cursor`, `plugins/claude`, and `plugins/codex`. There is no server and no web UI. Drive isolated copies. Never write `~/.cursor/plugins/local/plan-build-verify`, `~/.claude/plugins/`, or `~/.codex/plugins/` on the operator home.

Read `features/README.md` before the first drive.

## Launch

From the repo root:

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv launch
```

Ready when the command prints a run id, then a path under `uat-evidence/verify-plan-build-verify/`, and `evidence/launch.log` contains `wrote plugins/cursor, plugins/claude, plugins/codex`. That command runs `python3 scripts/build.py` and copies each host tree into the run's throwaway `home/`.

Export the printed run id as `VERIFY_PBV_RUN` for later commands, or pass `--run-id`.

## Doctor

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv doctor
```

Pass only when all of these hold:

- `python3 scripts/check.py` exits 0. Stdout is `plugin trees match src/ and host layout rules`.
- The run's Cursor, Claude, and Codex copies exist.
- Each copy has skills `plan`, `build`, `review`, `verify`, and `triage`.
- Each copy has only that host's plugin.json directory.

Run doctor before the first drive, after any failed drive, and whenever the trees look wrong. Do not drive a copy this run did not create.

## Drive

Use `control-pbv`. Treat every command as literal.

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive cursor-local-install
.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive claude-plugin
.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive codex-plugin
.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive documented-build
```

Stable handles:

- Skill directory names `plan`, `build`, `review`, `verify`, `triage` under `skills/`.
- Agent files `plan-agent.md`, `build-agent.md`, `verify-agent.md` under `agents/` on Cursor and Claude.
- Command files `commands/plan.md`, `commands/build.md`, `commands/verify.md` whose YAML `description` values are `Run the plan-build-verify Plan workflow`, `Run the plan-build-verify Build workflow`, and `Run the plan-build-verify Verify workflow`.
- Host manifests `.cursor-plugin/plugin.json`, `.claude-plugin/plugin.json`, and `.codex-plugin/plugin.json`.
- Codex must not have `agents/` or `commands/`. `.codex-plugin/` contains only `plugin.json`.

Follow the matching file under `features/` for the feature you are proving. Drive every entry point that file lists.

Do not run `claude plugin marketplace add`, `claude plugin install`, `codex plugin marketplace add`, or `codex plugin add` during an isolated run. Those commands write the operator host.

## Evidence

Proof lives at `uat-evidence/verify-plan-build-verify/$RUN_ID/evidence/`. That directory is gitignored. Keep it after cleanup.

Standards:

- Exercise the README install path that the feature map names. `control-pbv launch` runs `python3 scripts/build.py`. `control-pbv doctor` runs `python3 scripts/check.py`.
- Capture the command, stdout, stderr, and exit code, plus a second read of the installed copy (listing, `plugin.json`, command files).
- Installed-copy proof is the run `home/` listing and `plugin.json`. `scripts/check.py` on `plugins/` is the tree contract only.
- `claude plugin validate ./plugins/claude --strict` on the repo tree is the CI command. The Claude feature also validates the isolated copy.
- Live Cursor plugin UI and Claude plugin UI screenshots need a human host session. Record those as `verified-unreachable` with the missing session named. Do not pass a tree listing as that screenshot.

## Cleanup

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv cleanup
```

This removes only that run's `home/`. It does not delete `evidence/` or `run.json`. Kill nothing by process name. This product has no long-lived process.

After a failed iteration, run the same cleanup before the next launch so leftover plugin copies do not accumulate. Evidence from the failed run stays.

## Helpers

`scripts/control-pbv` is executable. Invoke it from the repo root.

```bash
.cursor/skills/verify-plan-build-verify/scripts/control-pbv launch
.cursor/skills/verify-plan-build-verify/scripts/control-pbv doctor
.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive cursor-local-install
.cursor/skills/verify-plan-build-verify/scripts/control-pbv cleanup
```

`launch` writes `run.json` with `run_id`, `home`, `cursor_install`, `claude_install`, `codex_install`, and `version`. Doctor and drive read that file. Do not invent paths.
