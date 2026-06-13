#!/usr/bin/env python3
"""Deterministic citation-integrity and bib-hygiene checker for a LaTeX/biblatex thesis.

Scans .tex files for \\cite-family keys and a .bib file for entries, then reports:
  - undefined: cited keys with no matching .bib entry (hard error)
  - duplicate: keys defined more than once in the .bib (hard error)
  - unused: .bib entries never cited (warning)
  - malformed: entries missing required fields or with a bad year (warning)

No third-party dependencies; uses only the standard library.

Usage:
  python check_citations.py --tex-dir thesis --bib thesis/bibliography.bib
  python check_citations.py            # defaults: scan ./ for *.tex, find first *.bib
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# \cite, \citep, \citet, \parencite, \textcite, \autocite, \footcite, \cites ...
CITE_RE = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")
ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)

# Minimal required fields per entry type for a credible bibliography.
REQUIRED = {
    "article": ["author", "title", "journal", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "incollection": ["author", "title", "booktitle", "year"],
    "book": ["author", "title", "publisher", "year"],
    "inbook": ["author", "title", "publisher", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "misc": ["title"],
    "online": ["title"],
    "unpublished": ["author", "title"],
}


def find_tex_files(tex_dir: Path) -> list[Path]:
    return sorted(p for p in tex_dir.rglob("*.tex"))


def collect_citations(tex_files: list[Path]) -> dict[str, list[str]]:
    """Return {key: [source files where cited]}."""
    cited: dict[str, list[str]] = {}
    for f in tex_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        # strip full-line comments to avoid counting commented-out cites
        text = re.sub(r"((?<!\\)(?:\\\\)*)%.*", r"\1", text)
        for m in CITE_RE.finditer(text):
            for key in m.group(1).split(","):
                key = key.strip()
                if key and key != "*":  # \nocite{*} means "all entries", not a real key
                    cited.setdefault(key, [])
                    if f.name not in cited[key]:
                        cited[key].append(f.name)
    return cited


def parse_bib(bib_path: Path):
    """Return (entries, duplicates).

    entries: {key: {"type": str, "fields": {name: value}}}
    duplicates: list of keys appearing more than once
    """
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    entries: dict[str, dict] = {}
    duplicates: list[str] = []
    seen: set[str] = set()

    for m in ENTRY_RE.finditer(text):
        etype = m.group(1).lower()
        key = m.group(2).strip()
        if etype in ("comment", "string", "preamble"):
            continue
        if key in seen:
            duplicates.append(key)
            continue
        seen.add(key)
        body = _entry_body(text, m.end())
        entries[key] = {"type": etype, "fields": _parse_fields(body)}
    return entries, duplicates


def _entry_body(text: str, start: int) -> str:
    """Return the brace-balanced body of an entry starting just after '{key,'."""
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    # field = value, where value is {...} or "..." or a bare token
    field_re = re.compile(r"(\w+)\s*=\s*", re.IGNORECASE)
    pos = 0
    while True:
        m = field_re.search(body, pos)
        if not m:
            break
        name = m.group(1).lower()
        vstart = m.end()
        if vstart >= len(body):
            break
        ch = body[vstart]
        if ch == "{":
            val, pos = _balanced(body, vstart, "{", "}")
        elif ch == '"':
            val, pos = _quoted(body, vstart)
        else:
            end = body.find(",", vstart)
            end = len(body) if end == -1 else end
            val, pos = body[vstart:end].strip(), end
        fields[name] = val.strip()
    return fields


def _balanced(body: str, start: int, open_c: str, close_c: str):
    depth = 0
    i = start
    while i < len(body):
        if body[i] == open_c:
            depth += 1
        elif body[i] == close_c:
            depth -= 1
            if depth == 0:
                return body[start + 1 : i], i + 1
        i += 1
    return body[start + 1 :], len(body)


def _quoted(body: str, start: int):
    i = start + 1
    while i < len(body):
        if body[i] == '"':
            return body[start + 1 : i], i + 1
        i += 1
    return body[start + 1 :], len(body)


def check_malformed(entries: dict[str, dict]) -> list[str]:
    problems: list[str] = []
    for key, e in sorted(entries.items()):
        req = REQUIRED.get(e["type"])
        fields = e["fields"]
        if req:
            missing = [f for f in req if f not in fields]
            if missing:
                problems.append(f"{key} ({e['type']}): missing {', '.join(missing)}")
        year = fields.get("year") or fields.get("date", "")[:4]
        if year and not re.fullmatch(r"\d{4}", year.strip()):
            problems.append(f"{key}: suspicious year '{year}'")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tex-dir", default=".", help="directory to scan for .tex (recursive)")
    ap.add_argument("--bib", default=None, help="path to .bib (default: first *.bib under tex-dir)")
    args = ap.parse_args()

    tex_dir = Path(args.tex_dir)
    if not tex_dir.is_dir():
        print(f"ERROR: Directory '{tex_dir}' does not exist or is not a directory", file=sys.stderr)
        return 2
    bib_path = Path(args.bib) if args.bib else next(iter(sorted(tex_dir.rglob("*.bib"))), None)
    if bib_path is None or not bib_path.exists():
        print("ERROR: no .bib file found", file=sys.stderr)
        return 2

    tex_files = find_tex_files(tex_dir)
    cited = collect_citations(tex_files)
    entries, duplicates = parse_bib(bib_path)

    defined = set(entries)
    used = set(cited)
    undefined = sorted(used - defined)
    unused = sorted(defined - used)
    malformed = check_malformed(entries)

    print(f"Scanned {len(tex_files)} .tex file(s); {len(used)} unique key(s) cited.")
    print(f"Bibliography: {bib_path} ({len(entries)} entries).\n")

    def section(title, items, fmt=str):
        print(f"## {title} ({len(items)})")
        for it in items:
            print(f"  - {fmt(it)}")
        if not items:
            print("  (none)")
        print()

    section("Undefined citations (cited, not in .bib)", undefined,
            lambda k: f"{k}  [cited in {', '.join(cited[k])}]")
    section("Duplicate keys in .bib", duplicates)
    section("Unused entries (in .bib, never cited)", unused)
    section("Malformed entries", malformed)

    hard_errors = len(undefined) + len(duplicates)
    if hard_errors:
        print(f"FAIL: {hard_errors} hard error(s) (undefined/duplicate).")
        return 1
    print("OK: no undefined or duplicate citations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
