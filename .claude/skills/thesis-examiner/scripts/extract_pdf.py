#!/usr/bin/env python3
"""Extract a thesis PDF to text with page markers so the examiner can cite pages.

Every page is prefixed with a line like `===== [page 12] =====` so that when you
write a finding you can point the student to an exact page. This is the single
most-repeated setup step in a thesis review, so it lives here once.

Usage:
    python extract_pdf.py path/to/thesis.pdf [-o out.txt]

If -o is omitted, text goes to stdout. Tries PyMuPDF (best layout + reliable
page boundaries), then falls back to the `pdftotext` CLI, then to pypdf.
"""
import argparse
import shutil
import subprocess
import sys


def via_pymupdf(path):
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    chunks = []
    for i, page in enumerate(doc, start=1):
        chunks.append(f"\n===== [page {i}] =====\n")
        chunks.append(page.get_text("text"))
    return "".join(chunks)


def via_pdftotext(path):
    # pdftotext emits a form-feed (\f) between pages with -layout; turn those
    # into explicit page markers so citations stay reliable.
    out = subprocess.run(
        ["pdftotext", "-layout", path, "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    pages = out.split("\f")
    chunks = []
    for i, body in enumerate(pages, start=1):
        if body.strip() == "" and i == len(pages):
            continue
        chunks.append(f"\n===== [page {i}] =====\n")
        chunks.append(body)
    return "".join(chunks)


def via_pypdf(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        chunks.append(f"\n===== [page {i}] =====\n")
        chunks.append(page.extract_text() or "")
    return "".join(chunks)


def extract(path):
    errors = []
    try:
        return via_pymupdf(path)
    except Exception as e:  # noqa: BLE001
        errors.append(f"pymupdf: {e}")
    if shutil.which("pdftotext"):
        try:
            return via_pdftotext(path)
        except Exception as e:  # noqa: BLE001
            errors.append(f"pdftotext: {e}")
    try:
        return via_pypdf(path)
    except Exception as e:  # noqa: BLE001
        errors.append(f"pypdf: {e}")
    raise SystemExit(
        "Could not extract text. Install one of: pymupdf, poppler-utils "
        "(pdftotext), or pypdf.\n  " + "\n  ".join(errors)
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    text = extract(args.pdf)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        words = len(text.split())
        print(f"Wrote {args.out} ({words:,} words).", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
