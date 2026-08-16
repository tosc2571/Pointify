---
name: tdd-workflow
description: Use when implementing a new functional requirement, bug fix, or GitHub issue in Pointify. Encodes the project's think-first, test-first, surgical-diff workflow (see the coding-guidelines and language-conventions skills) — clarify the requirement, write a failing test, implement the minimum to pass it, then verify with build-test before calling the work done. Skip only for genuinely trivial edits.
---

# Requirement → test → implementation

1. **Clarify.** Restate the requirement in one or two sentences. If more
   than one reasonable interpretation exists, list them and ask which one —
   don't silently pick. Name anything confusing before writing code. See the
   `coding-guidelines` skill for the full think-first/simplicity/surgical-diff
   discipline, and `language-conventions` for the German/English split.
2. **Locate the right layer.** Check [README.md](../../../README.md) and the
   existing `backend/app/{routers,schemas,models}` / `frontend/src/app/features`
   structure before assuming a new abstraction or dependency is needed.
3. **Red.** Write a failing test:
   - Backend: in `backend/tests/`, mirroring the module under test (e.g. a
     new route on `app/routers/themes.py` gets a test in `test_themes.py`).
   - Frontend: a `*.spec.ts` next to the component/service under test, using
     `HttpTestingController` for HTTP-backed services/components (see
     existing specs under `frontend/src/app/features/*` for the pattern).
4. **Green.** Write the minimum code to make it pass. No speculative
   parameters, no unrequested configurability, no error handling for cases
   that can't occur.
5. **Verify.** Run the `build-test` skill (`pytest` for backend changes,
   `ng build`/`ng test` for frontend changes — both if a change spans the
   API contract). Both must be clean before reporting the task done. For a
   UI change, also do a real browser check (`ng serve` + backend running
   locally) rather than relying on unit tests alone.
6. **Diff check.** Every changed line should trace to the requirement.
   Don't touch adjacent code, comments, or formatting that wasn't part of
   the request. If you spot unrelated dead code, mention it instead of
   deleting it.
