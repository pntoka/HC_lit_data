'''
Functions to extract captions from html/xml files from different publishers (RSC, Elsevier, ACS, Wiley, Springer, Nature, Science, Taylor and Francis, Frontiers, MDPI)
'''
from bs4 import BeautifulSoup
import re

def rsc_captions(soup):
    '''RSC, MDPI'''
    captions = []
    for cap in soup.find_all(["td"], class_=lambda c: c and "image_title" in c.lower()):
        captions.append(cap.get_text(strip=True))
    for cap in soup.find_all(["div", "p"], class_=lambda c: c and "caption" in c.lower()):
        captions.append(cap.get_text(strip=True))
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)
    return results

def tandf_captions(soup):
    captions = []
    for cap in soup.find_all(["div", "p"], class_=lambda c: c and "caption" in c.lower()):
        captions.append(cap.get_text(strip=True))
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)
    return results

def acs_captions(soup):
    '''ACS, Frontiers'''
    captions = []
    for fig in soup.find_all('figure', id = True):
        id = fig.get('id')
        if id.startswith('fig'):
            cap = fig.find('p').get_text(strip=True)
            captions.append(cap)
        elif id.startswith('sch'):
            scheme_label = fig.find("h2", class_="fig-label").get_text(strip=True)
            texts = []
            for p in fig.find_all("p"):
                for span in p.find_all("span", class_="fn-label"):
                    span.decompose()     # remove Scheme a/b/c
                txt = p.get_text(strip=True)
                if txt:
                    texts.append(txt)
            cap = scheme_label + " " + " ".join(texts)
            captions.append(cap)
    for tab in soup.find_all('div', class_='NLM_caption'):
        cap = tab.get_text(strip=True)
        captions.append(cap)
    captions = list(dict.fromkeys(captions)) 
    captions = [c for c in captions if c.lstrip().lower().startswith(("figure", "table"))]
    results = structure_figure_captions(captions)
    return results

def nature_captions(soup):
    captions = []
    for cap in soup.find_all("figcaption"):
        figure = cap.parent
        subcap = figure.find("div", {"data-test": "bottom-caption"})
        if subcap:
            p_tag = subcap.find("p")
            p_text = p_tag.get_text(separator=" ", strip=True) if p_tag else ""
            caption = cap.get_text(strip=True) + " " + p_text
            captions.append(caption)
        else:
            captions.append(cap.get_text(strip=True))
    for cap in soup.find_all("caption"):
        captions.append(cap.get_text(strip=True))
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)

    return results

def science_captions(soup):
    captions = []
    for cap in soup.find_all("figcaption"):
        text = cap.get_text(strip=True)
        text = text.replace('\xa0', '')
        captions.append(text)
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)

    return results

def wiley_captions(soup):
    captions = []
    for cap in soup.find_all(["header"], class_=lambda c: c and "caption" in c.lower()):
        captions.append(cap.get_text(strip=True))
    for cap in soup.find_all("figcaption"):
        text = cap.get_text(strip=True).replace('Open in figure viewerPowerPoint', '')
        captions.append(text)
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)
    return results

def springer_captions(soup):
    captions = []
    for cap in soup.find_all(["div"], class_=lambda c: c and "figure" in c.lower()):
        captions.append(cap.get_text(strip=True))
    for cap in soup.find_all("figcaption"):
        captions.append(cap.get_text(strip=True))
    captions = [c for c in captions if c.lstrip().lower().startswith(("fig.", "table"))] #remove strings that do not start with "Fig." or "Table"
    captions = [c for c in captions if len(c) >= 8]
    captions = list(dict.fromkeys(captions))
    results = structure_figure_captions(captions)
    return results

def elsevier_captions(soup):
    '''Elsevier, Springer'''
    valid_label = re.compile(r'^(Fig\.?|Figure|Table|Scheme)\b', re.IGNORECASE)
    captions = []
    for label in soup.find_all("ce:label"):
        figure_number = label.get_text(strip=True)
        if not valid_label.match(figure_number):
            continue
        caption_tag = label.find_next("ce:caption")
        if caption_tag:
            cap = figure_number + " " + caption_tag.get_text(strip=True)
            captions.append(cap)

    results = structure_figure_captions(captions)
    return results

def concat_strings(captions):
    tables_caps = []
    for c in captions:
        if c.lower().startswith('table'):
            tables_caps.append(c.strip())

    fig_caps = []
    for c in captions:
        if c not in tables_caps:
            fig_caps.append(c.strip())

    return tables_caps, fig_caps

def structure_figure_captions(captions):
    tables_caps, figures_caps = concat_strings(captions)
    results = []
    if figures_caps:
        result_figure = {
            "name": "Figures",
            "type": "captions",
            "content": figures_caps
        }
        results.append(result_figure)

    if tables_caps:
        result_tables = {
            "name": "Tables",
            "content": tables_caps
        }
        results.append(result_tables)

    return results





