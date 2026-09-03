# plan-build-verify verification map

This directory is the maintained source for verifying the installable plugin trees. Read this index before driving, then use the matching feature file as the recipe.

## Baseline preconditions

- Work from the git checkout that owns `scripts/build.py`.
- Install Python test extras with `python3 -m pip install -r requirements-dev.txt` when `scripts/check.py` needs `jsonschema`.
- Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv launch`, then `doctor`.
- Require doctor to print `ready`, the run id, and the three isolated install paths.
- Never drive `~/.cursor/plugins/local/plan-build-verify` or the operator `~/.claude/plugins` or `~/.codex/plugins` trees.

## Driving conventions

- Start every recipe from a launched, healthy run unless the feature says otherwise.
- Treat skill names, command descriptions, and plugin.json paths as literal.
- Run every drive through `control-pbv drive <feature>`.
- Restore nothing in the git tree. Launch may rewrite generated `plugins/` through `scripts/build.py`. That is the documented writer.
- Cleanup removes `home/`. It must leave `evidence/` in place.

## Proof and skip reporting

- Capture the command and the resulting installed copy, not only `scripts/check.py` on `plugins/`.
- Proof includes stdout, stderr, exit code, `listing.txt`, and `plugin.json` from the isolated copy.
- Mutation proof for build is a second read of the generated catalogs and the isolated copies.
- Record the feature id with every artifact under `evidence/<feature>/`.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped live host UI as verified through a filesystem listing.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with control-pbv` starts with `Preconditions:` and uses labeled bullets that pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable handles, required state, commands, and observable proof.

## Features

- [Documented build](./documented-build.md) covers `python3 scripts/build.py` writing the three host trees and the three marketplace catalogs.
- [Cursor local install](./cursor-local-install.md) covers the README copy into a throwaway `~/.cursor/plugins/local/plan-build-verify`.
- [Claude plugin](./claude-plugin.md) covers the Claude tree, command descriptions, and `claude plugin validate --strict`.
- [Codex plugin](./codex-plugin.md) covers the Codex tree with skills and no `agents/` or `commands/`.
