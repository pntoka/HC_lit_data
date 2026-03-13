# article_retrieve

Downloads full-text articles in HTML or XML format from a list of DOIs.

## Supported publishers

| Publisher | Format | Method |
|---|---|---|
| Elsevier | XML | Elsevier API (requires `ELSEVIER_API_KEY`) |
| Wiley | HTML or XML | Selenium (Firefox headless) |
| Springer | HTML | requests |
| Nature | HTML | Selenium (Firefox headless) |
| MDPI | HTML | Selenium (Firefox headless) |
| Taylor & Francis | HTML | Selenium (Firefox headless) |
| Frontiers | HTML | Selenium (Firefox headless) |
| ACS | HTML | Selenium (Chrome, authenticated — separate script) |
| RSC | HTML | Selenium (Chrome, authenticated — separate script) |

## Requirements

- `ELSEVIER_API_KEY` environment variable set (see root README)
- Firefox and geckodriver installed (for most publishers)
- Chrome installed (for ACS/RSC only)

## Usage

### Step 1 — Download all publishers except ACS and RSC

```bash
python doi_to_article.py \
    --doi_file /path/to/dois_select.txt \
    --save_dir /path/to/articles/
```

ACS and RSC DOIs are skipped and written to `acs_dois.txt` and `rsc_dois.txt` in `save_dir`.

### Step 2 — Download ACS and RSC articles

```bash
python acs_rsc_doi_to_article.py \
    --doi_file /path/to/acs_dois.txt \
    --save_dir /path/to/articles/ \
    --chrome_path /path/to/chrome \
    --chrome_data_dir /path/to/chrome/profile
```

A Chrome window will open. Log in to the publisher site when prompted, then press Enter to begin downloading.

## Outputs

- `<doi>.txt` — article HTML or XML content, one file per DOI
- `acs_dois.txt` — ACS DOIs for separate processing
- `rsc_dois.txt` — RSC DOIs for separate processing
- `article_downloader.log` — success/failure log
- `acs_rsc_downloader.log` — ACS/RSC success/failure log
