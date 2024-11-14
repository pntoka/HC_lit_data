import requests
import re


def get_link_from_doi(doi):
    '''
    Takes in a doi and returns the link to the article
    '''
    url = 'https://api.crossref.org/works/' + doi
    headers = {'accept': 'application/json'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception('Error: Could not retrieve article information')   # figure out handling bad requests for doi information
    all_links = [link['URL'] for link in r.json()['message']['link']]
    unique_links = list(set(all_links))
    return unique_links


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