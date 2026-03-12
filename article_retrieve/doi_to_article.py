'''
Script to download full text articles from a list of DOIs.

Usage:
    python doi_to_article.py --doi_file /path/to/dois.txt --save_dir /path/to/output

Requires the ELSEVIER_API_KEY environment variable to be set before running:
    export ELSEVIER_API_KEY=your_key_here
'''

import os
import sys
import argparse

import scraper_tools.scraper


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download full text articles from a list of DOIs'
    )
    parser.add_argument(
        '--doi_file', required=True,
        help='Path to file containing DOIs, one per line'
    )
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory to save downloaded articles'
    )
    args = parser.parse_args()

    elsevier_api_key = os.environ.get('ELSEVIER_API_KEY')
    if not elsevier_api_key:
        print("Error: ELSEVIER_API_KEY environment variable is not set.")
        print("Set it with: export ELSEVIER_API_KEY=your_key_here")
        sys.exit(1)

    scraper_tools.scraper.download_article_from_doi(
        args.doi_file, args.save_dir, elsevier_api_key
    )
