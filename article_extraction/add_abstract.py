'''Script to add abstracts to the text corpus JSON files by retrieving them from the Scopus API.'''
import json
import os
import re
import time
import requests
import xml.etree.ElementTree as ET
import warnings


def abstract_retrieve(doi, api_key):
    """Retrieve the abstract text for a given DOI using the Scopus API."""
    url = f"https://api.elsevier.com/content/abstract/doi/{doi}"
    try:
        headers = {
            "Accept": "text/xml",
            "X-ELS-APIKey": api_key
        }
        r = requests.get(url, stream=True, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.text
        else:
            raise ValueError(f"Failed to retrieve abstract for DOI {doi}: {r.status_code}")
    except requests.RequestException as e:
        raise ValueError(f"Error retrieving abstract for DOI {doi}: {e}")


def extract_abstract(xml_content):
    """Extract abstract text from a Scopus XML response string."""
    try:
        root = ET.fromstring(xml_content)
        namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "ce": "http://www.elsevier.com/xml/ani/common",
        }
        para = root.find(".//dc:description/abstract/ce:para", namespaces)
        if para is None:
            raise ValueError("No ce:para element found within dc:description.")
        abstract_text = "".join(para.itertext()).strip()
        return abstract_text
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML content: {e}")
