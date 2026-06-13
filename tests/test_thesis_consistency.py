"""Regression tests for thesis analysis: keep quoted numbers consistent with data.

Run with:  make test   (or)   uv run pytest tests/ -v

Two layers:
  Tier 1 (test_fraction_percent_*) — pure self-consistency: every "N/D" paired
    with "P%" in the thesis/docs must satisfy N/D == P%. No data dependency;
    catches typos like changing a count but not its percentage.
  Tier 2 (test_claim_*) — source-of-truth binding: each registered claim must
    still match its JSON data file, and the number must still appear verbatim in
    the documents that quote it. Catches drift when an experiment is re-run or a
    table is edited.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from conftest import DECISIONS, REPO_ROOT, THESIS_CHAPTERS, read_text
from thesis_claims import CLAIMS, Claim

# ---------------------------------------------------------------------------
# Tier 1: fraction <-> percent self-consistency
# ---------------------------------------------------------------------------

# A "N/D" fraction (D has 2-4 digits, so "1/2"-style ratios are ignored) sitting
# next to a "P%" in the inline prose idiom "N/D, P%" or "P% (N/D)". The separator
# is deliberately tight — only spaces, commas, parens, "~" and "\" — and never
# spans "|", "&" or a newline, so we do NOT pair numbers across table cells (those
# are covered exactly by the Tier-2 registry instead).
_SEP = r"[ \t,()~\\]{0,4}"
_FRAC = r"(\d+)\s*/\s*(\d{2,4})"
_PCT = r"(\d+(?:\.\d+)?)\s*\\?%"
FRAC_THEN_PCT = re.compile(_FRAC + _SEP + _PCT)
PCT_THEN_FRAC = re.compile(_PCT + _SEP + _FRAC)


def _tolerance_pp(pct_text: str) -> float:
    """Allowed gap = half a unit of the precision the author wrote, plus epsilon.

    "64%" (0 decimals) tolerates correct rounding to the nearest whole percent;
    "72.25%" (2 decimals) is held to ~0.005 pp. A transposed digit moves the value
    far more than half a ULP, so it is still caught. Precision is read from the raw
    string so that "64" stays 0-decimal (not "64.0").
    """
    decimals = len(pct_text.partition(".")[2])
    return 0.5 * 10 ** (-decimals) + 0.011


def _doc_files() -> list[Path]:
    return sorted(THESIS_CHAPTERS.glob("*.tex")) + sorted(DECISIONS.glob("*.md"))


def _adjacent_pairs(text: str) -> list[tuple[int, int, str]]:
    """Return (numerator, denominator, percent_text) for each inline frac/pct pair.

    percent is kept as the raw string so the tolerance can honour its precision.
    """
    pairs: list[tuple[int, int, str]] = []
    for m in FRAC_THEN_PCT.finditer(text):
        pairs.append((int(m.group(1)), int(m.group(2)), m.group(3)))
    for m in PCT_THEN_FRAC.finditer(text):
        pairs.append((int(m.group(2)), int(m.group(3)), m.group(1)))
    return pairs


@pytest.mark.parametrize(
    "doc", _doc_files(), ids=lambda p: str(p.name)
)
def test_fraction_percent_consistency(doc: Path) -> None:
    """Every "N/D" adjacent to a "P%" must satisfy round(N/D*100, 2) == P."""
    text = doc.read_text(encoding="utf-8")
    mismatches: list[str] = []
    for num, den, pct_text in _adjacent_pairs(text):
        if den == 0:
            continue
        actual = num / den * 100
        if abs(actual - float(pct_text)) > _tolerance_pp(pct_text):
            mismatches.append(
                f"{num}/{den} = {actual:.2f}% but text says {pct_text}%"
            )
    assert not mismatches, f"{doc.name}:\n  " + "\n  ".join(mismatches)


# ---------------------------------------------------------------------------
# Tier 2: claims must match their source data and the docs that quote them
# ---------------------------------------------------------------------------


def _matching_source(claim: Claim) -> dict:
    """Return the data of a file under the claim's glob that carries its count.

    Fails the test if no file reproduces the count, or if a matching file is
    internally inconsistent (accuracy != correct/total).
    """
    files = sorted(REPO_ROOT.glob(claim.source_glob))
    assert files, (
        f"{claim.claim_id}: glob '{claim.source_glob}' matched no files — the "
        f"result data moved or was deleted."
    )
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if (data.get("correct_count") == claim.correct
                and data.get("total_count") == claim.total):
            acc = data["accuracy"]
            assert abs(claim.correct / claim.total - acc) < 1e-6, (
                f"{claim.claim_id}: {path.name} is internally inconsistent "
                f"({claim.correct}/{claim.total} != accuracy {acc})."
            )
            return data
    pytest.fail(
        f"{claim.claim_id}: no file under '{claim.source_glob}' reports "
        f"{claim.correct}/{claim.total}. A re-run changed the result — update the "
        f"thesis numbers and this claim together."
    )


# data/output is gitignored (regenerable), so the reproduction check is a
# local-only guard: it runs on a machine that has the experiment outputs and is
# skipped in CI / fresh checkouts, where there is nothing to reproduce against.
_DATA_ROOT = REPO_ROOT / "data" / "output"
DATA_PRESENT = _DATA_ROOT.exists() and next(_DATA_ROOT.rglob("*.json"), None) is not None


@pytest.mark.skipif(
    not DATA_PRESENT,
    reason="data/output is gitignored; reproduction check runs only where the "
    "experiment outputs are present (e.g. locally / on HPC).",
)
@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c.claim_id)
def test_claim_reproduced_in_data(claim: Claim) -> None:
    """Some result file still reproduces the count the thesis reports."""
    _matching_source(claim)


@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c.claim_id)
def test_claim_quoted_in_docs(claim: Claim) -> None:
    """Each cited doc still quotes this claim's "correct/total" fraction.

    The fraction is the reliable anchor; the percentage's rounding/format is
    already validated by test_fraction_percent_consistency.
    """
    fraction = f"{claim.correct}/{claim.total}"
    for rel in claim.cited_in:
        text = read_text(rel)
        assert fraction in text, (
            f"{claim.claim_id}: '{fraction}' not found in {rel} — the document "
            f"no longer quotes the source-of-truth count."
        )
