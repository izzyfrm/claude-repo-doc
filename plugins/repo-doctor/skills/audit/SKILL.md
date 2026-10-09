---
name: audit
description: Analyze repository health, organization, configuration mistakes, merge conflicts, suspicious secret locations, and syntax errors. Use when asked to audit, inspect, check, or clean up a repository.
argument-hint: "[optional path]"
---

# Repository audit

Audit the user's repository using the included **read-only** scanner first.

1. Determine the repository root from the working directory. If `$ARGUMENTS` contains a path, treat it as user input: confirm the path exists and ask for clarification if it is ambiguous. Do not interpolate untrusted path text into shell syntax.
2. Run the scanner with a Python interpreter available on the user's system:
   - Windows: `py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/repo_audit.py" .` (or `python`)
   - macOS / Linux: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/repo_audit.py" .`
   - For machine-readable results, append `--json`.
   - Use an explicit path argument instead of `.` if the user specified one.
3. Summarize findings grouped by severity, quote file locations but NEVER print possible secrets or their values.
4. Distinguish scanner findings from additional findings you personally verified by reading the code. The scanner is heuristic, not a full security audit.
5. Recommend the smallest fixes with highest impact first. Make edits only after the user has requested changes. Never silently remove files or overwrite configuration.
6. If nothing is found, say the scanner found no issues within its limited checks, not that the project is secure.
