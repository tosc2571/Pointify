---
name: git-workflow
description: Use for any commit, push, pull-request, or GitHub issue work in Pointify. main is protected — no direct pushes for anyone, admins included; every change reaches main via a pull request with passing backend/frontend/smoke/docker checks. Encodes branching, commit style, the pre-push privacy check, GitHub issue conventions, and the recovery steps when commits accidentally land on local main.
---

# Git workflow (protected `main`)

Branch protection on `main` (set via `gh api`, applies to admins too):

- Direct pushes are rejected; force pushes and branch deletion are blocked.
- Pull requests are required (0 approvals — solo maintainer), with required
  status checks `backend`, `frontend`, `smoke`, and `docker`, and the branch
  must be up to date with `main` (`strict: true`).

## Normal flow

**No code change without a tracking issue and a PR — no exceptions.** Every
piece of work, however small (a one-line bug fix, a doc tweak), starts with
a `gh issue create` and lands via a pull request, never a direct commit
pushed straight through on a branch with no issue behind it. This applies
even when the user reports something informally in chat ("X is broken") —
create the issue first, then branch/implement/PR against it.

1. **Never commit on `main`.** Branch from the current remote state:
   `git fetch origin && git switch -c feat/<topic> origin/main`
2. **Commits:** English, imperative, conventional-commit prefix
   (`feat:`, `fix:`, `docs:`, `chore:`). Claude-authored commits end with the
   Co-Authored-By line from the harness guidelines.
   - **Never use literal backticks inside a double-quoted `-m` string** (or
     any other double-quoted Bash string) to reference a command or code
     snippet inline — bash treats backticks in double quotes as command
     substitution and will actually execute the enclosed text, silently
     splicing its output (often empty, or an error) into the message. Use
     single quotes for the shell string, or avoid inline backticked code in
     that context.
3. **Privacy check before every push** — the repo is public:
   - No `backend/.venv/`, `frontend/node_modules/`, `frontend/dist/`,
     `backend/app/static/` (the built-frontend copy), or `*.db`/`*.db-shm`/
     `*.db-wal` files tracked (`git status` after a broad `git add` should
     show none of these).
   - No hardcoded secrets — `SECRET_KEY` must come from configuration/env,
     never a literal string in source (this was a real issue in the
     pre-migration prototype; don't reintroduce it).
   - `git diff origin/main...HEAD` greps clean for anything that looks like
     a real credential, token, or personal data.
4. `git push -u origin feat/<topic>`
5. `gh pr create` — English title and body summarizing the change; the body
   ends with the Claude Code attribution line from the harness guidelines.
   - **Use a closing keyword for the tracked issue** (`Closes #N` /
     `Fixes #N`), not just a bare `(#N)` reference — a bare reference
     doesn't auto-close the issue on merge, leaving it stale-open even
     though the work is done.
6. Wait for `backend`, `frontend`, `smoke`, and `docker` to pass, then merge
   (`gh pr merge --merge`) and delete the branch.
   - **Sleep at least 60s before the first `gh pr checks`/`gh run list`
     call after pushing or creating a PR.** GitHub Actions can take a while
     to dispatch the workflow run; checking earlier reliably prints "no
     checks reported" even when everything is fine, which reads like a
     stuck/failed trigger it isn't. Don't chain shorter sleeps or retry
     loops to work around this — one 60s wait, then check.

## GitHub issues

- English, per [language-conventions](../language-conventions/SKILL.md) — even
  though the user writes to you in German.
- Match the house style visible in past issues (`gh issue list --repo
  tosc2571/Pointify --state all`, then `gh issue view <n>`): `## Goal`, then
  `## Proposed behavior` (with sub-sections as needed), `## Design notes`,
  `## Acceptance criteria` as a checklist, ending with the Claude Code
  attribution line from the harness guidelines.
- Check `--state all` (not just open) for related or duplicate issues before
  drafting, and cross-reference them (`#4`, `#5`, ...) where relevant.
- If the body includes implementation details the user didn't explicitly ask
  for (new endpoints, specific acceptance criteria, etc.), show the draft in
  chat and get a go-ahead before `gh issue create` — don't publish invented
  scope straight to a public repo. Skip this step only when the user's
  request already fully specifies the content or says to just create it.

## If commits accidentally landed on local `main`

A push from local `main` will be rejected by the protection. Move the work
to a branch instead of weakening the protection:

```bash
git switch -c feat/<topic>        # takes the local commits along
git branch -f main origin/main    # resets local main to the remote state
```

Then continue with the normal flow (privacy check → push → PR).
