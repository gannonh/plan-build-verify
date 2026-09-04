# Claude plugin

The Claude tree is `plugins/claude`. A Claude Code install surfaces skills `plan`, `build`, `review`, `verify`, and `triage`, agents `plan-agent`, `build-agent`, and `verify-agent`, and commands `/plan`, `/build`, and `/verify`. CI proves the tree with `claude plugin validate ./plugins/claude --strict`.

## Sub-features

- `claude-tree` keeps skills, agents, and commands in the Claude copy.
- `claude-commands` keeps the same three command descriptions as Cursor.
- `claude-validate` runs `claude plugin validate --strict` on the isolated copy.
- `claude-manifest` keeps only `.claude-plugin/plugin.json`.

## How to get to it (user POV)

- Run `claude plugin marketplace add gannonh/plan-build-verify`, then `claude plugin install plan-build-verify@plan-build-verify`.
- Run `claude plugin validate ./plugins/claude --strict` from this checkout.
- Open the Claude plugin UI or `claude plugin details plan-build-verify@plan-build-verify` on a live install.

## Driving it with control-pbv

Preconditions:

- A launched run whose doctor output is `ready`.
- `claude` is on `PATH`.
- The Claude install path is under that run's `home/`.

- **Stage copy.** Launch copied `plugins/claude` to `$HOME/.claude/plugins/cache/plan-build-verify/plan-build-verify/<version>/` inside the throwaway home. Read `run.json` `claude_install`.
- **Drive install.** Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive claude-plugin`. Exit code `0`. `evidence/claude-plugin/result.txt` is `ok`.
- **Validate.** `evidence/claude-plugin/validate.log` shows `claude plugin validate` on that isolated path with `--strict` and exit `0`.
- **Skills and agents.** `evidence/claude-plugin/listing.txt` lists skills `build, plan, review, triage, verify` and agents `build-agent.md, plan-agent.md, verify-agent.md`.
- **Commands.** `evidence/claude-plugin/commands/plan.md` contains `description: Run the plan-build-verify Plan workflow`. The Build and Verify files match their twins.
- **Proof.** `evidence/claude-plugin/plugin.json` has `"name": "plan-build-verify"`. The listing manifests line is `.claude-plugin` only.

## Gotchas

- Do not run `claude plugin marketplace add` or `claude plugin install` with `control-pbv`. Those commands write `~/.claude/plugins/known_marketplaces.json` and the operator cache.
- `claude` on this machine may be aliased. The helper uses `shutil.which("claude")`, so a shell alias is invisible. Put a real binary on `PATH`.
- Live Claude plugin UI is unreachable without a dedicated Claude session. Record it as `verified-unreachable` without that session.
- Claude agents use richer frontmatter than Cursor agents. Do not compare those files by hash across hosts.
- `claude plugin details` on a live install has reported Agents (0) while `agents/*.md` exist and `claude plugin validate --strict` passes. Isolated drive asserts the agent files on disk.
