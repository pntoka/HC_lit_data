# ARTICLE_RETRIEVE
Script for downloading full text articles in html or xml format using their DOI

## Usage
The downloading of articles from the following publishers is possible:
* Elsevier
* Wiley
* MDPI
* Springer Nature
* Taylor and Francis
* ACS
* RSC

To download articles first run the ```doi_to_article.py``` script. Fill in the script with the directory to save the articles and the path to the file containg the dois
```
save_dir = ''
file_path = ''
elsevier_api_key = ''
```
This script will download all articles except ones from ACS and RSC. The dois of articles from ACS and RSC are saved into *acs_dois.txt* and *rsc_dois.txt* in the specified save directory.

To download the ACS and RSC articles run the ```acs_rsc_doi_to_article.py``` script. A Chrome browser needs to be installed for this and the path to the application needs to be provided in the script.

```
save_dir = ''
file_path = ''
chrome_path = ''
```