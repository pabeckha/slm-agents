"""Convert a PDF file to Markdown using docling."""

from pathlib import Path

from docling.document_converter import DocumentConverter


def convert_pdf_to_md(pdf_path: str | Path, output_path: str | Path | None = None) -> Path:
    pdf_path = Path(pdf_path)
    if output_path is None:
        output_path = pdf_path.with_suffix(".md")
    output_path = Path(output_path)

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    markdown = result.document.export_to_markdown()

    output_path.write_text(markdown, encoding="utf-8")
    print(f"Converted {pdf_path} -> {output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    pdf = sys.argv[1] if len(sys.argv) > 1 else "docs/en.subject.pdf"
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert_pdf_to_md(pdf, out)
