# DOI_search
Script for searching and retrieving DOIs (digital object identifiers) based on a search query using Semantic Scholar or Crossref as the search engine.

## Usage
The details of the search query are contained in the query.toml file. The parameters fot the search such as the publication date ranges, search queries, publisher prefixes to select and which search engine to use are specified by modifying the query.toml file in the relevant field. 

To run the search run the doi_search.py file with the path of the query.toml file

```shell
python doi_search.py /PATH/TO/QUERY/TOML/FILE
```
