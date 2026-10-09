#!/usr/bin/env python3
"""Dependency-free, read-only repository preflight scanner.

This does not run project code or print secret values.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "dist", "build", "target", "__pycache__", ".next", ".nuxt",
    ".pytest_cache", ".mypy_cache", "coverage", ".turbo",
}
TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".jsonc",
    ".md", ".txt", ".html", ".css", ".scss", ".rs", ".lua",
    ".luau", ".toml", ".yaml", ".yml", ".sh", ".ps1", ".c",
    ".cpp", ".h", ".cs", ".go", ".xml", ".sql", ".gitignore",
}
MAX_FILES = 5000
MAX_TEXT_BYTES = 512 * 1024
MAX_ISSUES = 250


def audit(root: Path) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    findings: list[dict[str, Any]] = []
    examined = 0
    ignored = 0
    truncated = False
    total_bytes = 0
    ext_counts: dict[str, int] = {}

    def record(level: str, code: str, message: str, file: str = "", line: int | None = None) -> None:
        nonlocal truncated
        if len(findings) >= MAX_ISSUES:
            truncated = True
            return
        entry: dict[str, Any] = {"severity": level, "code": code, "message": message}
        if file:
            entry["file"] = file
        if line is not None:
            entry["line"] = line
        findings.append(entry)

    if not any((root / name).is_file() for name in ("README.md", "README.rst", "README.txt")):
        record("warning", "NO_README", "No README found in the repository root.")
    if not any((root / name).is_file() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")):
        record("info", "NO_LICENSE", "No top-level license file found.")
    if not (root / ".gitignore").exists():
        record("info", "NO_GITIGNORE", "No top-level .gitignore found.")

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(current) / d).is_symlink())
        for filename in sorted(files):
            path = Path(current) / filename
            if path.is_symlink():
                ignored += 1
                continue
            if examined >= MAX_FILES:
                truncated = True
                break
            try:
                stat = path.stat()
            except OSError:
                ignored += 1
                continue
            rel = path.relative_to(root).as_posix()
            examined += 1
            total_bytes += stat.st_size
            suffix = path.suffix.lower() or "[none]"
            ext_counts[suffix] = ext_counts.get(suffix, 0) + 1

            if filename == ".env" or filename.startswith(".env.") and filename not in (".env.example", ".env.sample", ".env.template"):
                record("warning", "ENV_FILE", "Environment file exists; verify it is not committed and is in .gitignore.", rel)
            if filename.lower().endswith((".pem", ".p12", ".pfx", ".key")):
                record("warning", "KEY_FILE", "Possible credential/key material; verify it is intentionally present and not public.", rel)
            if stat.st_size > 10 * 1024 * 1024:
                record("info", "LARGE_FILE", "File exceeds 10 MiB; consider whether it belongs in version control.", rel)
            if path.suffix.lower() not in TEXT_SUFFIXES and filename not in (".gitignore", ".env.example"):
                continue
            if stat.st_size > MAX_TEXT_BYTES:
                ignored += 1
                continue
            try:
                raw = path.read_bytes()
                if b"\0" in raw:
                    continue
                data = raw.decode("utf-8")
            except (OSError, UnicodeError):
                ignored += 1
                continue

            if path.suffix.lower() == ".py":
                try:
                    ast.parse(data, filename=rel)
                except SyntaxError as exc:
                    record("error", "PYTHON_SYNTAX", f"Python syntax error: {exc.msg}", rel, exc.lineno)
            elif path.suffix.lower() == ".json":
                try:
                    json.loads(data)
                except json.JSONDecodeError as exc:
                    record("error", "INVALID_JSON", f"Invalid JSON: {exc.msg}", rel, exc.lineno)

            for line_no, line in enumerate(data.splitlines(), 1):
                stripped = line.lstrip()
                if stripped.startswith(("<<<<<<< ", "=======", ">>>>>>> ")):
                    # For separators, require the standard seven-character merge divider.
                    if stripped.startswith("=======") and stripped.strip() != "=======":
                        continue
                    record("error", "MERGE_MARKER", "Possible unresolved merge conflict marker.", rel, line_no)
                # Report only one trailing-whitespace finding per file.
            if any(line.endswith((" ", "\t")) for line in data.splitlines()):
                record("info", "TRAILING_WHITESPACE", "File contains trailing whitespace.", rel)
        if examined >= MAX_FILES:
            break

    rank = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda x: (rank[x["severity"]], x.get("file", ""), x.get("line", 0), x["code"]))
    return {
        "root": str(root),
        "files_examined": examined,
        "files_skipped_or_unreadable": ignored,
        "total_bytes": total_bytes,
        "file_types": dict(sorted(ext_counts.items(), key=lambda item: (-item[1], item[0]))[:12]),
        "issues": findings,
        "truncated": truncated,
        "disclaimer": "Heuristic, read-only checks only; not a full security review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path("."), help="Repository to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    try:
        result = audit(args.path)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Repo Doctor — {result['root']}")
        print(f"Files: {result['files_examined']} | Findings: {len(result['issues'])} | Limited: {result['truncated']}")
        for issue in result["issues"]:
            where = issue.get("file", "repository")
            if "line" in issue:
                where += f":{issue['line']}"
            print(f"[{issue['severity'].upper()}] {issue['code']} — {where}: {issue['message']}")
        print(result["disclaimer"])
    return 1 if any(f["severity"] == "error" for f in result["issues"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
