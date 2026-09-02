---
name: verify
description: Use this skill when proving completed work meets a spec issue's acceptance criteria. Runs the plan-build-verify Verify workflow with bundled user-acceptance, a pull request, CI convergence, and a signoff recommendation. Never merges the PR.
---

# Verify

Validate completed implementation against the spec issue's acceptance criteria, publish the evidence, open the pull request, and drive it to green.

## Read the conventions first

Read `references/conventions.md` completely before any write.

## When to use

- The issue is `status:implemented`, or Build just completed and entered this workflow.
- The user asks for UAT, signoff, merge readiness, or proof that work is complete.

## Verify workflow

Read `references/verify.md` completely and follow it.

User-acceptance evidence:

1. Look for a project-local `verify-*` skill first and follow it when present.
2. Read `references/user-acceptance/workflow.md` completely and follow it for the evidence contract.
3. Use scripts under `scripts/user-acceptance/`.
4. Do not generate a verification skill during Verify.

Review-thread inventory uses the sibling `address-pr-comments` skill in this plugin. If that skill is not available, read threads with `gh api graphql` as described in `references/verify.md`.

Hard gates:

- Verify must not claim signoff without evidence.
- Verify must never merge the PR. Signoff and merge are the user's decision.
- Verify opens the PR. The PR body carries the acceptance-criteria matrix.
- Never check off a criterion without evidence in the matrix.
- Never edit the wording of an acceptance criterion to make it pass.

## Shared principles

- Keep Verify tied to the approved acceptance criteria.
- A push is never a terminal state.
- A single green snapshot while checks are still queued is never a terminal state.
- Never drop a review comment without a posted disposition.
