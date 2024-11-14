import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import logging
import scraper_tools.link as link
from scraper_tools.utils import read_doi_file, make_batches
import time

PUB_PREFIX = {"RSC": "10.1039", "ACS": "10.1021", "Nature":"10.1038", "Science":"10.1126", "Frontiers":"10.3389", "MDPI":"10.3390", "Wiley": "10.1002", "Springer":"10.1007", "TandF":"10.1080", "Elsevier":"10.1016", 'IOP': '10.1088'}


def setup_logger(name, log_file, level=logging.INFO):
    '''
    Function to set up logger
    '''
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class FullTextDownloader:
    def __init__(self, pub_prefix, api_key):
        self.pub_prefix = pub_prefix
        self.api_key = api_key

    def downloadElsevier(self, doi, save_dir):
        if not os.path.exists(save_dir):
            print(
                f"{save_dir} directory does not exists.\nCreating directory {save_dir}"
            )
            os.makedirs(save_dir)

        article_url = "https://api.elsevier.com/content/article/doi/" + doi
        article = requests.get(
            article_url,
            headers={
                "x-els-apikey": self.api_key,
                "Content-Type": "application/xml",
                },
        )
        if article.status_code == 200:
            with open(os.path.join(save_dir, f"{doi.replace('/','-')}.txt"), "w+", encoding='utf-8') as f:
                f.write(article.text)
            return True
        elif article.status_code != 200:
            print('Error: ', article.status_code, f'for {doi}')
            return False

    def link_selector(self, doi, pdf=False):
        prefix = doi[:7]
        links = link.get_link_from_doi(doi)

        if prefix == PUB_PREFIX["RSC"]:
            return link.rsc_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["ACS"]:
            return link.acs_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["Wiley"]:
            return link.wiley_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["Springer"]:
            return link.springer_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["Frontiers"]:
            return link.frontiers_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["MDPI"]:
            return link.mdpi_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["Nature"]:
            return link.nature_link_selector(doi, links, pdf)
        elif prefix == PUB_PREFIX["TandF"]:
            return link.tandf_link_selector(doi, links, pdf)

    def web_scrape_html(self, doi, link, save_dir):
        '''
        Function to scrape full text html from link using selenium webdriver
        '''
        opts = Options()
        opts.add_argument("--headless")
        # options.binary_location = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"      #stuff for webdriver to work on windows laptop
        # driver = webdriver.Firefox(executable_path=r"C:\Users\Piotr\geckodriver.exe", options=options)
        driver = webdriver.Firefox(options=opts)
        driver.get(link)
        driver.implicitly_wait(5)
        page = driver.page_source.encode('utf-8')
        with open(os.path.join(save_dir, f"{doi.replace('/','-')}.txt"), "wb") as save_file:
            save_file.write(page)
        driver.close()


def springer_scrape_html(self, doi, save_dir):
    '''
    Function get page source from springer link using requests
    '''
    base_url = 'https://link.springer.com/article/'
    api_url = base_url + doi
    headers = {
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0'
    }
    r = requests.get(api_url, stream=True, headers=headers, timeout=30)
    if r.status_code == 200:
        with open(os.path.join(save_dir, f"{doi.replace('/','-')}.txt"), "wb") as f:
            f.write(r.content)
        return True
    elif r.status_code != 200:
        print('Error: ', r.status_code, f'for {doi}')
        return False
    

def article_downloader(dois, save_dir, elsevier_api_key, pdf=False):
    '''
    Function to download full text articles from list of dois
    '''
    log = setup_logger('log', save_dir)
    downloader = FullTextDownloader(PUB_PREFIX, elsevier_api_key)
    for doi in dois:
        if doi[:7] == PUB_PREFIX['Elsevier']:
            result = downloader.downloadElsevier(doi, save_dir)
            if result is False:
                log.info(f'Error with downloading: {doi}')
        elif doi[:7] == PUB_PREFIX['Springer']:
            result = downloader.springer_scrape_html(doi, save_dir)
            if result is False:
                log.info(f'Error with downloading: {doi}')
        else:
            link = downloader.link_selector(doi, pdf)
            if link is not None:
                downloader.web_scrape_html(doi, link, save_dir)
            if link is None:
                print(f'No link found for {doi}')
                log.info(f'Error with downloading: {doi}')


def download_article_from_doi(file_path, save_dir, elsevier_api_key, pdf=False, batch_size=50):
    '''
    Function to download full text articles from a file containing dois
    '''
    dois = read_doi_file(file_path)
    doi_batches = make_batches(dois, batch_size)
    for i, batch in enumerate(doi_batches):
        print(f'Downloading batch {i+1} of {len(doi_batches)}')
        article_downloader(batch, save_dir, elsevier_api_key, pdf)
        time.sleep(10)