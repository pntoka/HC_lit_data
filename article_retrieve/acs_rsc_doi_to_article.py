'''
Script to download full text ASC or RSC articles from a list of dois
'''

import scraper_tools.scraper
import scraper_tools.utils

if __name__ == '__main__':
    save_dir = ''
    file_path = ''
    chrome_path = '' # Path to Chrome executable
    scraper_tools.utils.open_chrome(chrome_path)
    while True:
        input("Login to RSC or ACS and press Enter to continue.")
        break
    scraper_tools.scraper.download_acs_rsc_from_doi(file_path, save_dir)