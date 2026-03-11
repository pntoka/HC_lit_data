'''
Extract sections matching user-supplied keywords from JSON article files and
write them as Markdown.

Matching is case-insensitive substring search against section names, so
keyword "experimental" will match "Experimental", "Experimental Section",
"Experimental details", etc.  Multiple keywords are OR-combined, so
["experimental", "methods", "methodology"] matches any section whose name
contains at least one of those words.

When a section matches it is included in full (all nested subsections).
Non-matching top-level sections are recursed into so that a matching
sub-section can still be found.

Usage
-----
    python article_extraction/json_section_extract.py \\
        --data_dir  /path/to/json_articles \\
        --save_dir  /path/to/output \\
        --keywords  experimental methods methodology

'''

import json
import os
import sys
import argparse
from pathlib import Path


# ── Heading level helpers (mirrored from json_to_md.py) ───────────────────────

_TYPE_TO_LEVEL = {
    'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6,
}


def _heading_level(section_type: str, depth: int) -> int:
    """Return Markdown heading level (1–6) for *depth* inside the document.

    Explicit HTML-like types (h2, h3, …) take precedence; otherwise depth
    drives the level with top-level sections (depth=0) rendered as ##.
    """
    if section_type in _TYPE_TO_LEVEL:
        return _TYPE_TO_LEVEL[section_type]
    return min(depth + 2, 6)


# ── Keyword matching ───────────────────────────────────────────────────────────

def _matches(name: str, keywords: list[str]) -> bool:
    """Return True if *name* contains any keyword (case-insensitive)."""
    name_lower = name.lower()
    return any(kw.lower() in name_lower for kw in keywords)


# ── Section extraction ─────────────────────────────────────────────────────────

def extract_matching_sections(
    sections: list,
    keywords: list[str],
) -> list[dict]:
    """Return section objects whose name matches *keywords*.

    Walks the section tree depth-first.  When a section matches it is
    collected in full (including all nested content).  Non-matching sections
    are recursed into so deeply-nested matches are still found.

    Both Variant A (list of dicts) and Variant B (list of strings) are
    handled.
    """
    matched: list[dict] = []

    for item in sections:
        if isinstance(item, str):
            # Variant B flat paragraph – nothing to match against
            continue

        if isinstance(item, dict):
            name = item.get('name', '')
            content = item.get('content', [])

            if _matches(name, keywords):
                matched.append(item)
            else:
                # Recurse into subsections
                matched.extend(extract_matching_sections(content, keywords))

    return matched


# ── Markdown rendering ─────────────────────────────────────────────────────────

def _section_to_lines(section: dict, depth: int = 0) -> list[str]:
    """Render a single section object (and all its content) as Markdown lines."""
    lines: list[str] = []

    name = section.get('name', '').strip()
    section_type = section.get('type', '')
    content = section.get('content', [])

    if name:
        level = _heading_level(section_type, depth)
        lines.append(f"{'#' * level} {name}")
        lines.append('')

    for item in content:
        if isinstance(item, str):
            text = item.strip()
            if text:
                lines.append(text)
                lines.append('')
        elif isinstance(item, dict):
            lines.extend(_section_to_lines(item, depth + 1))

    return lines


def build_md(data: dict, matched_sections: list[dict]) -> str:
    """Compose the full Markdown string for *matched_sections* of *data*.

    Always includes the paper metadata header (title, DOI, journal, keywords,
    abstract) followed by only the matched sections.
    """
    lines: list[str] = []

    # might be useful later
    # ── Abstract ───────────────────────────────────────────────────────────
    # abstract = data.get('Abstract', '').strip()
    # if abstract:
    #     lines.append('## Abstract')
    #     lines.append('')
    #     lines.append(abstract)
    #     lines.append('')

    # ── Matched sections ───────────────────────────────────────────────────
    for section in matched_sections:
        lines.extend(_section_to_lines(section, depth=0))

    md = '\n'.join(lines)
    if not md.endswith('\n'):
        md += '\n'
    return md


# ── Public API ─────────────────────────────────────────────────────────────────

def extract_sections_to_md(json_path: str, keywords: list[str]) -> str | None:
    """Read *json_path* and return Markdown containing only the sections whose
    name matches *keywords*.

    Returns ``None`` when no sections match (so callers can skip the file).
    """
    with open(json_path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    sections = data.get('Sections', [])
    matched = extract_matching_sections(sections, keywords)

    if not matched:
        return None

    return build_md(data, matched)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'Extract keyword-matched sections from JSON article files '
            'and save them as Markdown.'
        )
    )
    parser.add_argument(
        '--data_dir',
        required=True,
        help='Directory containing the JSON article files.',
    )
    parser.add_argument(
        '--save_dir',
        default=None,
        help=(
            'Directory to save Markdown files '
            '(default: <parent of data_dir>/section_extracts).'
        ),
    )
    parser.add_argument(
        '--keywords',
        nargs='+',
        required=True,
        metavar='KEYWORD',
        help=(
            'One or more keywords to match against section names '
            '(case-insensitive substring match).  '
            'E.g. --keywords experimental methods methodology'
        ),
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    keywords: list[str] = args.keywords

    # ── Validate input directory ────────────────────────────────────────────
    if not os.path.exists(data_dir):
        print(f"Error: data directory '{data_dir}' does not exist.")
        sys.exit(1)

    # ── Resolve / create output directory ──────────────────────────────────
    save_dir = args.save_dir
    if save_dir is None:
        parent_dir = os.path.dirname(os.path.abspath(data_dir))
        save_dir = os.path.join(parent_dir, 'section_extracts')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    # ── Discover JSON files ─────────────────────────────────────────────────
    json_files = sorted(f for f in os.listdir(data_dir) if f.endswith('.json'))

    if not json_files:
        print(f"No JSON files found in '{data_dir}'.")
        return

    print(f"Found {len(json_files)} JSON file(s) in '{data_dir}'")
    print(f"Keywords: {keywords}")
    print('-' * 80)

    successful = 0
    skipped = 0
    failed: list[str] = []

    for filename in json_files:
        json_path = os.path.join(data_dir, filename)
        md_filename = Path(filename).stem + '.md'
        md_path = os.path.join(save_dir, md_filename)

        try:
            md_content = extract_sections_to_md(json_path, keywords)
            if md_content is None:
                print(f" SKIP  {filename}  — no matching sections")
                skipped += 1
                continue

            with open(md_path, 'w', encoding='utf-8') as fh:
                fh.write(md_content)
            print(f"   OK  {filename}  →  {md_filename}")
            successful += 1

        except Exception as exc:
            print(f" FAIL  {filename}  —  {exc}")
            failed.append(filename)

    # ── Summary ────────────────────────────────────────────────────────────
    print('-' * 80)
    print(
        f"Complete: {successful} converted, {skipped} skipped "
        f"(no match), {len(failed)} failed  /  {len(json_files)} total."
    )
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")


if __name__ == '__main__':
    main()
