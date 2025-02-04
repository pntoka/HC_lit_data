'''Functions for selecting the correct link for each publisher'''

import requests
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_doi(doi):
    '''
    Validates if DOI matches expected format:
    - Starts with '10.'
    - Followed by 4-9 digits (DOI manual does not set a max digits limit but in practice it is 9)
    - Followed by '/' and additional characters
    '''
    doi_pattern = r'^10.\d{4,9}/[-._;()/:\w]+$'
    return bool(re.match(doi_pattern, doi))

def get_link_from_doi(doi):
    '''
    Takes in a doi and returns the link to the article:
    1. Validates DOI format
    2. Makes API request to crossref.org
    3. Extracts and returns unique article URLs
    4. Handles errors and logs failures
    '''
    if not validate_doi(doi):
        logger.error(f"Invalid DOI format: {doi}")
        _log_failed_doi(doi, "Invalid DOI format")
        return None
        
    url = 'https://api.crossref.org/works/' + doi
    headers = {'accept': 'application/json'}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        
        all_links = [link['URL'] for link in r.json()['message']['link']]
        unique_links = list(set(all_links))
        return unique_links
        
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (e.g. 404, 500)
        logger.error(f"HTTP Error for DOI {doi}: {str(e)}")
        _log_failed_doi(doi, f"HTTP Error: {r.status_code}")
        return None
    except Exception as e:
        # Handle any other errors
        logger.error(f"Error processing DOI {doi}: {str(e)}")
        _log_failed_doi(doi, str(e))
        return None

def _log_failed_doi(doi, reason):
    '''Log failed DOIs to a file'''
    with open('failed_urls.txt', 'a') as f:
        f.write(f"DOI: {doi}, Reason: {reason}\n")

# Code below is unchanged from Piotr's original code

def link_checker(part, links):
    '''
    Function to check if a link contains a certain fragment
    '''
    for link in links:
        if part in link:
            return link
    return None


def acs_link_selector(doi, links, pdf=False):
    part = 'pubs.acs.org/doi/pdf'
    link = link_checker(part, links)
    if pdf:
        return link
    if link is not None:
        link = re.sub('pdf/', '', link)
        return link
    else:
        link = 'https://pubs.acs.org/doi/' + doi  # html link
    return link


def rsc_link_selector(doi, links, pdf=False):
    part = 'pubs.rsc.org/en/content/articlepdf'
    link = link_checker(part, links)
    if pdf:
        return link
    if link is not None:
        link = re.sub('articlepdf', 'articlehtml', link)    
    return link


def wiley_link_selector(doi, links, pdf=False):
    if pdf:
        part = 'onlinelibrary.wiley.com/doi/pdf'
        link = link_checker(part, links)
        if link is not None:
            return link
    part = 'onlinelibrary.wiley.com/doi/full-xml'
    link = link_checker(part, links)
    if link is not None:
        return link
    part = 'doi/pdf'
    link = link_checker(part, links)
    if link is not None:
        link = re.sub('pdf/', '', link)
    return link


def frontiers_link_selector(doi, links, pdf=False):
    if pdf and links[0] is not None:
        link = re.sub('full', 'pdf', links[0])
        return link
    if links[0] is not None:
        return links[0]
    return None


def mdpi_link_selector(doi, links, pdf=False):
    part = '/pdf'
    link = link_checker(part, links)
    if pdf:
        return link
    if link is not None:
        link = re.sub('/pdf', '', link)
    return link  # html link


def springer_link_selector(doi, links, pdf=False):
    if pdf:
        part = 'content/pdf'
        link = link_checker(part, links)
        if link is not None:
            return link
    part = '/fulltext.html'
    link = link_checker(part, links)
    if link is not None:
        return link
    part = '.pdf'
    link = link_checker(part, links)
    if link is not None:
        link = re.sub('.pdf', '', link)
    return link


def nature_link_selector(doi, links, pdf=False):
    part = '.pdf'
    link = link_checker(part, links)
    if pdf:
        return link
    if link is not None:
        link = re.sub('.pdf', '', link)
    return link


def tandf_link_selector(doi, links, pdf=False):
    part = 'tandfonline.com/doi/pdf'
    link = link_checker(part, links)
    if pdf:
        return link
    if link is not None:
        link = re.sub('pdf/', '', link)
    return link