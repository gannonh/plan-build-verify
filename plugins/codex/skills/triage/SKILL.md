---
name: triage
description: Use this skill when grooming the GitHub issue backlog or answering what to work on next. Runs the plan-build-verify Triage workflow. Description-triggered. Never runs automatically from Plan, Build, or Verify.
---

# Triage

Groom the issue backlog so the roadmap stays readable and every spec issue is in a state Build or Verify can act on.

## Read the conventions first

Read `references/conventions.md` completely before any write.

## When to use

- The user asks to groom the backlog or the roadmap.
- The user asks what should we work on next.
- Plan, Build, or Verify reported hygiene findings that need fixing.

Triage is on-demand. It never runs automatically. Plan, Build, and Verify perform a lightweight read-only hygiene check at phase entry and report findings; fixing them is this workflow's job.

## Triage workflow

Read `references/triage.md` completely and follow it.

Hard gates:

- Report findings before mutating anything.
- Apply tier-1 safe corrections directly. Ask before tier-2 changes. Never do tier-3 work without explicit instruction.
- Do not treat adopted type labels (`enhancement`, `feature`, `bug`) as plan-build-verify defects.

## Shared principles

- An issue whose `status:*` label does not match its `## Status` section is a triage defect.
- Prefer the next user-facing slice when ranking ready work.
- Surface uncertainty instead of filling gaps with guesses.
