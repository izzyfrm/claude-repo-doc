# Repo Doctor

**Repository health checks and release prep for Claude Code.**

A lightweight Claude Code plugin with real analysis code, no API keys, no third-party dependencies, and no automatic edits. Built by [Isaiah Boyd](https://github.com/izzyfrm).

## Features

| Skill | What it does |
| --- | --- |
| `/repo-doctor:audit` | Scans the repository for missing docs, suspect credentials, invalid JSON, invalid Python, merge conflicts, large files, and trailing whitespace. |
| `/repo-doctor:review` | Reviews staged and unstaged changes for correctness, regressions, and missing tests. |
| `/repo-doctor:ship` | Creates a release-readiness report with test, docs, version, and Git checks. |

Also includes a `reliability-reviewer` subagent for independent reviews. The audit skill runs a real stdlib-only Python CLI. Reviews and release workflows are conducted by Claude using repository context.

## Install

Requires **Claude Code** and **Python 3.9+** on your machine for the audit scanner.

### Install from GitHub (after this repository has been published)

```powershell
claude plugin marketplace add izzyfrm/claude-repo-doctor
claude plugin install repo-doctor@izzy-devtools
```

Open Claude Code in any project and use `/repo-doctor:audit`, `/repo-doctor:review`, or `/repo-doctor:ship`.

### Try from a local folder (no publication required)

From the unzipped repository directory:

```powershell
claude --plugin-dir ./plugins/repo-doctor
```

### Install from a local marketplace

```powershell
claude plugin validate .
claude plugin marketplace add .
claude plugin install repo-doctor@izzy-devtools
```

If you are already inside a Claude Code session, start a new session or run `/reload-plugins` to load new skills.

## Use the scanner without Claude Code

Windows:

```powershell
py -3 .\plugins\repo-doctor\scripts\repo_audit.py . --json
```

macOS / Linux:

```sh
python3 ./plugins/repo-doctor/scripts/repo_audit.py . --json
```

The CLI exits `1` if an error-level finding is found, `0` otherwise, and `2` for invalid usage.

## Development

```powershell
python -m unittest discover -s tests -v
claude plugin validate .
claude plugin validate ./plugins/repo-doctor
```

The test suite uses `unittest` from the standard library.

## Design principles

- Read-only audit by default; no silent edits, pushes, installs, or deployments.
- No network connections, tokens, or external services required.
- Never emit environment variable values or the contents of key files.
- Keep findings actionable and distinguish heuristic warnings from proven bugs.
- Cross-platform plugin skills; Python interpreter command differs between Windows and Unix.

## Limitations

This is a fast heuristic scanner, **not** a dedicated security audit, type checker, or language server. It does not evaluate JavaScript, Rust, Luau, or C# syntax. It only reads up to 512 KiB per text file, inspects up to 5,000 files, and caps reported findings. Review results from Claude depend on project context and available tools.

## License

MIT. See [LICENSE](LICENSE).
