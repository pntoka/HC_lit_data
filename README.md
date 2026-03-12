# HC_lit_data

Pipeline for searching, retrieving, and extracting scientific literature data from multiple publishers. The pipeline consists of three sequential stages:

```
DOI_retrieve  →  article_retrieve  →  article_extraction
  (search)         (download)            (parse to JSON)
```

Supported publishers: Elsevier, ACS, RSC, Wiley, Springer, Nature, Taylor & Francis, MDPI, Frontiers, Science.

---

## Setup

### 1. Python environment

Requires Python >= 3.11. Install dependencies with [uv](https://github.com/astral-sh/uv) (recommended) or pip:

```bash
uv sync
# or
pip install -e .
```

### 2. LimeSoup (required for Elsevier and RSC extraction)

LimeSoup must be installed manually from its GitHub repository. Before installing, the `setup.py` must be modified to remove the hard-pinned `BeautifulSoup` version (change `beautifulsoup4==4.9.3` to `beautifulsoup4>=4.9.3`).

```bash
git clone https://github.com/CederGroupHub/LimeSoup.git
cd LimeSoup
# Edit setup.py: change  beautifulsoup4==4.9.3  →  beautifulsoup4>=4.9.3
pip install .
```

### 3. Environment variables

The Elsevier/Scopus API key is required for:
- Downloading Elsevier full-text articles (`article_retrieve`)
- Retrieving article abstracts via the Scopus API (`article_extraction`)

Set it in your shell before running any script that needs it:

```bash
export ELSEVIER_API_KEY=your_key_here
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) to make it permanent.

---

## Stage 1 — DOI search (`DOI_retrieve/`)

Searches Semantic Scholar or Crossref for DOIs matching a configurable set of queries and publisher filters.

**Configure** the search by editing [`DOI_retrieve/query.toml`](DOI_retrieve/query.toml):

| Field | Description |
|---|---|
| `pub_dates` | Year range to search (e.g. `[2010, 2024]`) |
| `queries` | List of search strings |
| `save_dir` | Output directory for DOI files |
| `pub_type` | Publication type filter (e.g. `"JournalArticle"`) |
| `pub_skip` | Publication type to exclude (e.g. `"Review"`) |
| `prefix_list` | Publisher DOI prefixes to keep |
| `engine` | `"semantic_scholar"` or `"crossref"` |

**Run:**

```bash
# Use the engine specified in query.toml
python DOI_retrieve/doi_retrieve.py DOI_retrieve/query.toml

# Force Semantic Scholar only
python DOI_retrieve/doi_sem_scholar.py DOI_retrieve/query.toml

# Force Crossref only
python DOI_retrieve/doi_crossref.py DOI_retrieve/query.toml
```

**Outputs** (written to `save_dir`):
- `<query_name>/doi_all.txt` — raw DOIs per query
- `doi_unique.txt` — deduplicated DOIs across all queries
- `dois_select.txt` — DOIs filtered to the configured publisher prefixes

---

## Stage 2 — Article download (`article_retrieve/`)

Downloads full-text articles in HTML or XML format using a list of DOIs.

### Most publishers (Elsevier, Wiley, Springer, Nature, MDPI, Taylor & Francis, Frontiers)

Requires `ELSEVIER_API_KEY` to be set (see Setup).

```bash
python article_retrieve/doi_to_article.py \
    --doi_file /path/to/dois_select.txt \
    --save_dir /path/to/articles/
```

ACS and RSC DOIs that require authenticated access are automatically separated and saved as `acs_dois.txt` and `rsc_dois.txt` in `save_dir`.

### ACS and RSC (authenticated download)

Requires a Chrome browser installation. Chrome is launched with remote debugging enabled so you can log in before scraping begins.

```bash
python article_retrieve/acs_rsc_doi_to_article.py \
    --doi_file /path/to/acs_dois.txt \
    --save_dir /path/to/articles/ \
    --chrome_path /path/to/chrome \
    --chrome_data_dir /path/to/chrome/profile
```

You will be prompted to log in to ACS or RSC in the opened Chrome window before scraping proceeds.

**Output:** one `.txt` file per article, named by DOI with `/` replaced by `-` (e.g. `10.1016-j.carbon.2017.12.103.txt`).

---

## Stage 3 — Article extraction (`article_extraction/`)

Parses downloaded article files and produces structured JSON.

```bash
python article_extraction/article_to_json.py \
    --data_dir /path/to/articles/ \
    --save_dir /path/to/json_output/
```

Requires `ELSEVIER_API_KEY` for abstract retrieval (skipped automatically with a warning if not set).

### Options

| Flag | Description |
|---|---|
| `--skip_extras` | Skip captions, tables, and figure URL extraction |
| `--skip_abstract` | Skip abstract retrieval from the Scopus API |

### Additional utilities

Convert JSON files to Markdown:

```bash
python article_extraction/json_to_md.py \
    --data_dir /path/to/json_output/ \
    --save_dir /path/to/markdown/
```

Extract only sections that match keywords:

```bash
python article_extraction/json_section_extract.py \
    --data_dir /path/to/json_output/ \
    --save_dir /path/to/sections/ \
    --keywords experimental methods
```

---

## Output JSON format

Each article is saved as `<doi>.json`.

### Top-level fields

```json
{
    "DOI":      "<string>  — DOI of the paper",
    "Journal":  "<string>  — journal name (may be empty)",
    "Title":    "<string>  — full paper title",
    "Abstract": "<string>  — abstract text (populated by add_abstract.py)",
    "Keywords": ["<string>", "..."],
    "Sections": "<see variants below>",
    "Figure_captions": ["<string>", "..."],
    "Table_captions":  ["<string>", "..."],
    "Tables": [
        {"label": "<string>", "content": "<table HTML string>"}
    ],
    "Figure_urls": ["<string>", "..."]
}
```

`Abstract`, `Figure_captions`, `Table_captions`, `Tables`, and `Figure_urls` are added automatically during extraction (see Stage 3 options above).

### `Sections` variants

The `Sections` field takes one of two forms depending on how the paper was extracted.

**Variant A — structured sections** (most publishers): an array of section objects.

```json
"Sections": [
    {
        "name":    "<string>  — section heading",
        "type":    "section",
        "content": [
            "<string>  — paragraph text",
            { "name": "...", "type": "section", "content": ["..."] }
        ]
    }
]
```

`content` may contain plain strings **or** nested section objects of the same shape, allowing arbitrary depth.

**Variant B — flat sections** (some publishers): an array of plain strings, one per paragraph.

```json
"Sections": [
    "<string>  — paragraph text",
    "..."
]
```
