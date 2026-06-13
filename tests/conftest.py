"""Shared test helpers for thesis-consistency regression tests."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THESIS_CHAPTERS = REPO_ROOT / "thesis" / "chapters"
DECISIONS = REPO_ROOT / "docs" / "decisions"


def load_json(rel_path: str | Path) -> dict:
    """Load a JSON file given a repo-root-relative path."""
    path = REPO_ROOT / rel_path
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def read_text(rel_path: str | Path) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")
