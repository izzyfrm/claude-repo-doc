---
name: ship
description: Prepare a repository for release using read-only checks of tests, docs, versioning, changes, and packaging. Use when asked whether a project is ready to ship or publish.
argument-hint: "[optional version]"
---

# Release readiness

Treat this as a **dry run** unless the user explicitly asks to publish or push.

1. Determine the repository's actual stack and release procedure by inspecting its files and README. Don't assume npm or Python.
2. Run `git status --short` and `git diff --check` if in a Git working tree. Explain any uncommitted changes.
3. Run the read-only audit: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/repo_audit.py" .` (use `py -3` or `python` on Windows).
4. Find existing build/test/lint commands from repository config; ask before running commands likely to write, delete, deploy, or alter user data. Run safe checks if available. Do not invent passing test results.
5. Check README quick start, environment variable documentation (without displaying values), version/changelog, dependency pinning, and license when applicable.
6. Report `Ready`, `Needs work`, or `Blocked`; provide a short, ordered release checklist with evidence and remaining risks.
7. Never push, tag, publish, deploy, or change version numbers merely because the skill was invoked. Those actions require explicit user intent.
