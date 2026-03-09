'''
Script to convert JSON article files to Markdown format.

Each JSON file is converted to a Markdown file preserving the Title, DOI,
Journal, Keywords, Abstract, and Sections hierarchy.  Heading levels are
derived either from the explicit section type (h2 → ##, h3 → ###, …) or,
for generic types such as ce_section, from the nesting depth.
'''

import json
import os
import sys
import argparse
from pathlib import Path


# Map explicit HTML-like heading types to Markdown heading levels
_TYPE_TO_LEVEL = {
    'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6,
}


def _heading_level(section_type: str, depth: int) -> int:
    """Return the Markdown heading level (1–6) for a section.

    If the section type is an explicit heading tag (h2, h3, …) that level is
    used directly.  Otherwise the nesting depth drives the level, with
    top-level sections (depth=0) rendered as ## (level 2) so that level 1 is
    reserved for the document title.
    """
    if section_type in _TYPE_TO_LEVEL:
        return _TYPE_TO_LEVEL[section_type]
    return min(depth + 2, 6)


def _sections_to_lines(sections: list, depth: int = 0) -> list[str]:
    """Recursively convert a Sections list to Markdown lines.

    Each element is either:
      • a plain string  → a paragraph
      • a dict          → a (possibly nested) section object
    """
    lines: list[str] = []

    for item in sections:
        if isinstance(item, str):
            text = item.strip()
            if text:
                lines.append(text)
                lines.append('')

        elif isinstance(item, dict):
            name = item.get('name', '').strip()
            section_type = item.get('type', '')
            content = item.get('content', [])

            if name:
                level = _heading_level(section_type, depth)
                lines.append(f"{'#' * level} {name}")
                lines.append('')

            if content:
                lines.extend(_sections_to_lines(content, depth + 1))

    return lines


def json_to_md(json_path: str) -> str:
    """Read a single JSON article file and return its Markdown representation."""
    with open(json_path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    lines: list[str] = []

    # ── Title ──────────────────────────────────────────────────────────────
    title = data.get('Title', '').strip()
    if title:
        lines.append(f'# {title}')
        lines.append('')

    # ── Metadata (DOI / Journal) ────────────────────────────────────────────
    doi = data.get('DOI', '').strip()
    journal = data.get('Journal', '').strip()
    if doi:
        lines.append(f'**DOI:** {doi}')
    if journal:
        lines.append(f'**Journal:** {journal}')
    if doi or journal:
        lines.append('')

    # ── Keywords ───────────────────────────────────────────────────────────
    keywords = data.get('Keywords', [])
    if keywords:
        lines.append('**Keywords:** ' + ', '.join(str(k) for k in keywords))
        lines.append('')

    # ── Abstract ───────────────────────────────────────────────────────────
    abstract = data.get('Abstract', '').strip()
    if abstract:
        lines.append('## Abstract')
        lines.append('')
        lines.append(abstract)
        lines.append('')

    # ── Sections ───────────────────────────────────────────────────────────
    sections = data.get('Sections', [])
    if sections:
        lines.extend(_sections_to_lines(sections, depth=0))

    # Ensure a single trailing newline
    md = '\n'.join(lines)
    if not md.endswith('\n'):
        md += '\n'
    return md


def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON article files to Markdown format'
    )
    parser.add_argument(
        '--data_dir',
        required=True,
        help='Directory containing the JSON article files',
    )
    parser.add_argument(
        '--save_dir',
        default=None,
        help='Directory to save Markdown files (default: <parent of data_dir>/markdown_articles)',
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    save_dir = args.save_dir

    # ── Validate input directory ────────────────────────────────────────────
    if not os.path.exists(data_dir):
        print(f"Error: data directory '{data_dir}' does not exist.")
        sys.exit(1)

    # ── Resolve / create output directory ──────────────────────────────────
    if save_dir is None:
        parent_dir = os.path.dirname(os.path.abspath(data_dir))
        save_dir = os.path.join(parent_dir, 'markdown_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    # ── Discover JSON files ─────────────────────────────────────────────────
    json_files = sorted(f for f in os.listdir(data_dir) if f.endswith('.json'))

    if not json_files:
        print(f"No JSON files found in '{data_dir}'.")
        return

    print(f"Found {len(json_files)} JSON file(s) in '{data_dir}'")
    print('-' * 80)

    successful = 0
    failed: list[str] = []

    for filename in json_files:
        json_path = os.path.join(data_dir, filename)
        md_filename = Path(filename).stem + '.md'
        md_path = os.path.join(save_dir, md_filename)

        try:
            md_content = json_to_md(json_path)
            with open(md_path, 'w', encoding='utf-8') as fh:
                fh.write(md_content)
            print(f"  OK  {filename}  →  {md_filename}")
            successful += 1
        except Exception as exc:
            print(f"FAIL  {filename}  —  {exc}")
            failed.append(filename)

    # ── Summary ────────────────────────────────────────────────────────────
    print('-' * 80)
    print(f"Complete: {successful}/{len(json_files)} file(s) converted successfully.")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")


if __name__ == '__main__':
    main()
