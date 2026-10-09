---
name: review
description: Review git diffs for bugs, regressions, risky assumptions, missing tests, and maintainability problems. Use before merging code or when asked for a code review.
argument-hint: "[optional scope]"
---

# Focused code review

1. Check the repository's working tree and whether `git` is available. Prefer `git diff --check`, `git diff`, and `git diff --cached` to determine the actual changes. If the changes are uncommitted, include both staged and unstaged changes; account for new untracked files separately.
2. Read nearby call sites, types, and tests to establish expected behavior. Do not make assumptions from a diff fragment alone.
3. Focus on bugs, correctness, injection/auth failures, data loss, portability, error handling, and missing tests. Avoid speculative lint feedback.
4. Output findings in priority order: `P0` critical, `P1` high, `P2` medium, `P3` low. For each finding include exact file and line and a concrete fix. If no issues were verified, state that plainly and mention review limitations.
5. Do **not** modify code as part of review unless explicitly requested.
6. Never publish secret content in the report; redact tokens and credentials.
