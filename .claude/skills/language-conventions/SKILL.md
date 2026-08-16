---
name: language-conventions
description: Use whenever writing or editing anything that becomes part of the Pointify project — code, identifiers, comments, commit messages, GitHub issues/PRs, documentation. Clarifies the German/English split (no exceptions currently, unlike FinFlow's tax-category labels).
---

# Language conventions

Conversation with the user happens in German. Everything that becomes part
of the project itself — code, identifiers, comments, commit messages,
GitHub issues/PRs, documentation, and user-facing UI text — is written in
**English**.

Unlike FinFlow (which keeps German tax-category labels since they map
directly to line items on an actual German tax return), Pointify has no
current exception: the rebuilt frontend and API error messages are English
throughout. If the user later wants German end-user-facing copy (e.g. for a
German-speaking audience), treat that as a deliberate, explicitly-confirmed
exception to document here — don't introduce German UI text unilaterally.

For the test-first implementation workflow, see the `tdd-workflow` skill.
