#!/usr/bin/env python3
"""Prepare markdown files for import into doccano.

Converts a directory of .md files into a JSONL file compatible with doccano's
sequence labeling import format. Each .md file becomes a single JSONL entry
containing the full file text. The markdown text is kept as-is. The DOI
(filename without extension) is added as a metadata field on each entry.

Output format:
    {"text": "Some paragraph text.", "label": [[0, 20, "10.1016-j.example"]]}

Usage:
    python prepare_import.py <input_dir> <output_file>

Example:
    python prepare_import.py test_data/input_methods_extract/ \
        output/doccano.jsonl
"""

import argparse
import json
from pathlib import Path


def file_to_entries(md_path: Path) -> list[dict]:
    """Convert a single markdown file into one doccano JSONL entry.

    The full file text is kept as-is. The filename (DOI) is stored as a
    metadata field so the source document is traceable during annotation.
    """
    doi = md_path.stem  # e.g. "10.1016-j.mtsust.2022.100313"
    doi_label = doi.replace("-", "/")  # e.g. "10.1016-j.mtsust.2022.100313"
    raw = md_path.read_text(encoding="utf-8").strip()
    return [{"text": raw, "doi": doi_label}]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a directory of markdown files to a"
            " doccano JSONL import file."
        )
    )
    parser.add_argument(
        "--input_dir",
        type=Path,
        help=(
            "Directory containing .md files"
            " (one file per article, filename = DOI)."
        ),
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        help="Path for the output .jsonl file.",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        raise SystemExit(f"Error: input directory not found: {args.input_dir}")

    md_files = sorted(args.input_dir.glob("*.md"))
    if not md_files:
        raise SystemExit(f"Error: no .md files found in {args.input_dir}")

    args.output_file.parent.mkdir(parents=True, exist_ok=True)

    total_entries = 0
    with args.output_file.open("w", encoding="utf-8") as out_f:
        for md_file in md_files:
            entries = file_to_entries(md_file)
            for entry in entries:
                out_f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            total_entries += len(entries)
            print(f"  {md_file.name:50s} → {len(entries)} entries")

    print(f"\nTotal: {total_entries} entries written to {args.output_file}")


if __name__ == "__main__":
    main()
