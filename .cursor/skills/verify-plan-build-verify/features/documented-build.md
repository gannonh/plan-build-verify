# Documented build

The documented build reads `src/` and writes the Cursor, Claude, and Codex plugin trees plus the three marketplace catalogs. That is the only supported writer of those paths.

## Sub-features

- `build-run` runs `python3 scripts/build.py` from a clean checkout.
- `build-trees` writes `plugins/cursor`, `plugins/claude`, and `plugins/codex`.
- `build-catalogs` writes `.cursor-plugin/marketplace.json`, `.claude-plugin/marketplace.json`, and `.agents/plugins/marketplace.json`.
- `build-stage` copies those trees into the run's throwaway home.

## How to get to it (user POV)

- Run the README Build command `python3 scripts/build.py`.
- Run `control-pbv launch`, which runs that same command and stages isolated copies.

## Driving it with control-pbv

Preconditions:

- The working tree is the plan-build-verify checkout.
- `scripts/build.py` exists.
- `control-pbv doctor` has passed for this run.

- **Run build.** Launch the verification run. Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv launch`. Exit code `0`. Printed lines are a run id and a directory under `uat-evidence/verify-plan-build-verify/`.
- **Confirm writer output.** Read `evidence/launch.log`. It contains `wrote plugins/cursor, plugins/claude, plugins/codex` and the three `wrote ... marketplace.json` lines. Exit code in that log is `0`.
- **Confirm catalogs.** Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive documented-build`. Exit code `0`. `evidence/documented-build/result.txt` is `ok`. The three marketplace files exist in the checkout.
- **Proof.** Open `evidence/documented-build/launch.log` and `evidence/launch.log`. Both show the same writer lines. The isolated Cursor, Claude, and Codex copies exist on paths printed by doctor.

## Gotchas

- `scripts/build.py` wipes `plugins/` before it writes. A dirty hand edit under `plugins/` is lost.
- `scripts/check.py` with the default git-clean gate fails if generated paths drift from git. Doctor runs that command. Run against a committed candidate. Preserve unrelated edits and correct authoring source before regenerating.
- Assert skill `review`. No `ship` entry point remains.
