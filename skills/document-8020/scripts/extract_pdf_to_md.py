#!/usr/bin/env python3
"""
Extract PDF text to a markdown file using pdfplumber.
Usage: python3 extract_pdf_to_md.py <pdf_path> [--output <md_path>]

Strips repeated headers/footers (page numbers, doc title lines) and
writes clean, page-separated markdown to /tmp/ by default.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not found. Run: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract_lines(pdf_path: str) -> list[list[str]]:
    """Return list of line-lists, one per page."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines()]
            pages.append(lines)
    return pages


def detect_boilerplate(pages: list[list[str]], threshold: float = 0.6) -> set[str]:
    """Lines that appear on more than `threshold` fraction of pages are boilerplate."""
    total = len(pages)
    if total == 0:
        return set()
    counter: Counter = Counter()
    for page_lines in pages:
        for line in set(page_lines):  # set: count once per page
            counter[line] += 1
    return {line for line, count in counter.items() if count / total >= threshold and line}


_FOOTER_PATTERN = re.compile(
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\s*\d{0,4}$",
    re.IGNORECASE,
)

def is_page_number(line: str) -> bool:
    stripped = line.strip()
    return bool(re.fullmatch(r"\d{1,4}", stripped)) or bool(_FOOTER_PATTERN.match(stripped))


def pages_to_markdown(pages: list[list[str]], boilerplate: set[str]) -> str:
    parts = []
    for i, lines in enumerate(pages, start=1):
        clean = [
            ln for ln in lines
            if ln not in boilerplate and not is_page_number(ln) and ln
        ]
        if clean:
            parts.append(f"\n\n---\n<!-- page {i} -->\n\n" + "\n".join(clean))
    return "\n".join(parts).strip()


def main():
    parser = argparse.ArgumentParser(description="Extract PDF to markdown via pdfplumber")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--output", help="Output .md path (default: /tmp/<stem>.md)")
    parser.add_argument(
        "--boilerplate-threshold",
        type=float,
        default=0.6,
        help="Fraction of pages a line must appear on to be treated as boilerplate (default: 0.6)",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output) if args.output else Path("/tmp") / (pdf_path.stem + ".md")

    print(f"Extracting: {pdf_path.name} ...", file=sys.stderr)
    pages = extract_lines(str(pdf_path))
    print(f"  {len(pages)} pages read", file=sys.stderr)

    boilerplate = detect_boilerplate(pages, threshold=args.boilerplate_threshold)
    if boilerplate:
        print(f"  Stripping {len(boilerplate)} boilerplate line(s): {list(boilerplate)[:5]}", file=sys.stderr)

    md = pages_to_markdown(pages, boilerplate)
    out_path.write_text(md, encoding="utf-8")

    char_count = len(md)
    word_count = len(md.split())
    print(f"  Written to: {out_path}", file=sys.stderr)
    print(f"  Size: {char_count:,} chars / ~{word_count:,} words", file=sys.stderr)
    # Print path to stdout for capture by caller
    print(out_path)


if __name__ == "__main__":
    main()
