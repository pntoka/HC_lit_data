'''
Script to download full text articles from a list of dois
'''

import scraper_tools.scraper

if __name__ == '__main__':
    save_dir = ''
    file_path = ''
    elsevier_api_key = ''
    scraper_tools.scraper.download_article_from_doi(file_path, save_dir, elsevier_api_key)