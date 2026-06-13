#!/usr/bin/env python3
"""Extract a fetchable source identifier for each cited .bib entry.

Emits JSON the agent uses to drive the grounding flow (see
references/citation-grounding.md): for every key actually cited in the .tex,
report the best way to retrieve the real source — arXiv id, URL, or a
title+author+year query for academic search.

Usage:
  python extract_sources.py --tex-dir thesis [--bib thesis/bibliography.bib]
  python extract_sources.py --tex-dir thesis --only ch:background   # not implemented; filter in agent
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_citations import collect_citations, find_tex_files, parse_bib  # noqa: E402

ARXIV_RE = re.compile(r"arxiv[:\s]*([0-9]{4}\.[0-9]{4,5})", re.IGNORECASE)


def arxiv_id(entry: dict) -> str | None:
    f = entry["fields"]
    if f.get("eprinttype", "").lower() in ("arxiv", "arxiv.org") and f.get("eprint"):
        m = re.search(r"([0-9]{4}\.[0-9]{4,5})", f["eprint"])
        if m:
            return m.group(1)
    blob = " ".join(f.get(k, "") for k in ("journal", "eprint", "note", "title", "url", "howpublished"))
    m = ARXIV_RE.search(blob)
    return m.group(1) if m else None


def first_author(author: str) -> str:
    if not author:
        return ""
    author = re.sub(r"[{}]", "", author)
    first = author.split(" and ")[0].strip()
    if "," in first:  # "Last, First"
        return first.split(",")[0].strip()
    return first.split()[-1] if first.split() else first  # surname is last token


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tex-dir", default=".")
    ap.add_argument("--bib", default=None)
    args = ap.parse_args()

    tex_dir = Path(args.tex_dir)
    bib_path = Path(args.bib) if args.bib else next(iter(sorted(tex_dir.rglob("*.bib"))), None)
    if not bib_path or not bib_path.exists():
        print("ERROR: no .bib found", file=sys.stderr)
        return 2

    cited = collect_citations(find_tex_files(tex_dir))
    entries, _ = parse_bib(bib_path)

    out = []
    for key in sorted(cited):
        e = entries.get(key)
        if not e:
            out.append({"key": key, "resolve": "MISSING", "note": "no .bib entry"})
            continue
        f = e["fields"]
        aid = arxiv_id(e)
        url = f.get("url") or _url_from_howpublished(f.get("howpublished", ""))
        record = {
            "key": key,
            "title": _clean(f.get("title", "")),
            "author": first_author(f.get("author", "")),
            "year": (f.get("year") or f.get("date", ""))[:4],
            "cited_in": cited[key],
        }
        if aid:
            record["resolve"] = "arxiv"
            record["arxiv"] = aid
            record["fetch"] = f"https://arxiv.org/abs/{aid}"
        elif url:
            record["resolve"] = "url"
            record["fetch"] = url
        else:
            record["resolve"] = "title"
            record["query"] = f"{record['title']} {record['author']} {record['year']}".strip()
        out.append(record)

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


def _url_from_howpublished(hp: str) -> str:
    m = re.search(r"\\url\{([^}]+)\}", hp) or re.search(r"(https?://\S+)", hp)
    return m.group(1) if m else ""


def _clean(s: str) -> str:
    return re.sub(r"[{}]", "", s).strip()


if __name__ == "__main__":
    sys.exit(main())
