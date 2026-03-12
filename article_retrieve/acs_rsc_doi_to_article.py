'''
Script to download full text ACS or RSC articles from a list of DOIs.
Requires a Chrome browser installation with remote debugging support.

Usage:
    python acs_rsc_doi_to_article.py \
        --doi_file /path/to/acs_rsc_dois.txt \
        --save_dir /path/to/output \
        --chrome_path /path/to/chrome \
        --chrome_data_dir /path/to/chrome/profile
'''

import argparse

import scraper_tools.scraper
import scraper_tools.utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download ACS and RSC articles using Chrome remote debugging'
    )
    parser.add_argument(
        '--doi_file', required=True,
        help='Path to file containing ACS/RSC DOIs, one per line'
    )
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory to save downloaded articles'
    )
    parser.add_argument(
        '--chrome_path', required=True,
        help='Path to Chrome executable'
    )
    parser.add_argument(
        '--chrome_data_dir', required=True,
        help='Path to Chrome user data directory'
    )
    args = parser.parse_args()

    scraper_tools.utils.open_chrome(args.chrome_path, args.chrome_data_dir)
    while True:
        input("Login to RSC or ACS in the Chrome window and press Enter to continue.")
        break
    scraper_tools.scraper.download_acs_rsc_from_doi(args.doi_file, args.save_dir)
