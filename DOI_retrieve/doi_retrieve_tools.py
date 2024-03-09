"""
Functions to retrieve DOIs using semantic scholar API
"""

import requests
import time
import os


def sem_scholar_bulk(query, pub_dates, use_token=False):
    """
    Function that takes a query and pub dates and does a bulk search for DOIs
    returns json of API response
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    headers = {"content-type": "application/json"}
    params = {
        "query": "{query}".format(query=query),
        "year": "{year}".format(year=pub_dates),
        "limit": 1000,
        "fields": "externalIds,publicationTypes",
    }
    if use_token is not False:
        params.update({"token": use_token})
    response = requests.get(base_url, headers=headers, params=params)
    count = 0
    while response.status_code != 200:
        print("Error: " + str(response.status_code) + " trying request again, attempt " + str(count + 1))
        time.sleep(30)
        response = requests.get(base_url, headers=headers, params=params)
        count += 1
        if count == 10:
            break
    print("Request successful for pub date = {pub_dates} and query = {query}".format(
        pub_dates=pub_dates, query=query))
    data = response.json()
    return data


def bulk_search_doi_pubtype(query, pub_dates):
    """
    Function that takes a query and pub dates and returns a dict of DOIs and pubtypes
    """
    data = sem_scholar_bulk(query, pub_dates)
    doi_dict = {}
    for paper in data["data"]:
        if "DOI" in paper["externalIds"]:
            doi_dict[paper["externalIds"]["DOI"]] = paper["publicationTypes"]
    while data["token"] is not None:
        data = sem_scholar_bulk(query, pub_dates, data["token"])
        for paper in data["data"]:
            if "DOI" in paper["externalIds"]:
                doi_dict[paper["externalIds"]["DOI"]] = paper["publicationTypes"]
        time.sleep(1)
    return doi_dict


def doi_dict_filter(doi_dict, pub_type, pub_skip):
    """
    Function that takes a doi dictionary and a publication type and returns
    a list of DOIs that match the publication type without the publication type to skip
    """
    doi_list = []
    for doi, pub_types in doi_dict.items():
        if pub_types is None:
            doi_list.append(doi)
        elif pub_type in pub_types and pub_skip not in pub_types:
            doi_list.append(doi)
    return doi_list


def storeDOI(dois, save_dir):  # Function to save list of dois to file
    with open(save_dir + "doi_all.txt", "a", encoding="utf-8") as save_file:
        for doi in dois:  # saves dois to doi.txt file with each doi on new line
            save_file.write(doi + "\n")


def get_dois_sem_sch(query, pub_dates, save_dir):
    """
    Function that take a query and pub dates and saves in a file the DOIs found
    """
    doi_dict = bulk_search_doi_pubtype(query, pub_dates)
    doi_list = doi_dict_filter(doi_dict, "JournalArticle", "Review")
    storeDOI(doi_list, save_dir)


def doi_search(query_list, pub_dates, save_dir):
    """
    Function that takes a list of queries, a range of ublication dates and a directory to save the results
    and returns a list of DOIs in a file. Results for each query are saved in a different directory
    """
    for query in query_list:
        save_dir_results = save_dir + query.replace(" ", "_") + "/"
        os.mkdir(save_dir_results)
        get_dois_sem_sch(query, pub_dates, save_dir_results)
        time.sleep(5)


def doi_unique(query_list, save_dir):
    """
    Function that goes through search results for different queries and returns a list of unique DOIs that is saved in a file
    """
    doi_list = []
    for query in query_list:
        folder = save_dir + query.replace(" ", "_") + "/"
        if os.path.exists(folder + "doi_all.txt") is False:
            continue
        else:
            with open(folder + "doi_all.txt", "r", encoding="utf-8") as file:
                dois = file.read().splitlines()
            doi_list.extend(dois)
    doi_list_unique = list(
        set(doi_list)
    )  # removes duplicates and leaves only unique dois
    with open(save_dir + "doi_unique.txt", "a", encoding="utf-8") as save_file:
        for (
            doi
        ) in doi_list_unique:  # saves dois to doi.txt file with each doi on new line
            save_file.write(doi + "\n")


def parse_query(query_file):
    with open(query_file, "r") as file:
        query_list = file.read().splitlines()
    pub_dates = query_list[0].split(" ")
    pub_dates = pub_dates[0] + "-" + pub_dates[1]
    search_queries = query_list[1:]
    return pub_dates, search_queries


def parse_args(args):
    """
    Function to parse command line arguments
    """
    query_file = args[0]
    save_dir = args[1]
    pub_dates, query_list = parse_query(query_file)
    return pub_dates, query_list, save_dir


def filter_dois(file, prefixes, save_dir):
    """
    Function to filter DOIs from a file
    """
    with open(os.path.join(save_dir, file), "r", encoding="utf-8") as f:
        dois = f.read().splitlines()
    filtered_dois = []
    for doi in dois:
        for prefix in prefixes:
            if doi.startswith(prefix):
                filtered_dois.append(doi)
    with open(os.path.join(save_dir, "dois_select.txt"), "a", encoding="utf-8") as f:
        for doi in filtered_dois:
            f.write(doi + "\n")


def crossref_search(
    pub_date, query, prefix, pub_type="journal-article", use_cursor="*"
):
    """
    Function to search crossref for journal article DOIs from specified prefix and publication date
    """
    base_url = "https://api.crossref.org/prefixes/{prefix}/works"
    headers = {"Accept": "application/json"}
    params = {
        "filter": f"from-pub-date:{pub_date},type:{pub_type}",
        "rows": 1000,
        "query": query,
        "select": "DOI",
        "cursor": use_cursor,
    }
    if use_cursor != "*":
        params.update({"cursor": use_cursor})
    response = requests.get(
        base_url.format(prefix=prefix), headers=headers, params=params
    )
    data = response.json()
    return data


def crossref_search_paging(pub_date, query, prefix, pub_type="journal-article"):
    """
    Function to search crossref for journal article DOIs from specified prefix and publication date
    """
    data = crossref_search(pub_date, query, prefix, pub_type)
    all_dois = []
    if data["status"] == "ok":
        all_dois.extend(
            [doi for doi_dict in data["message"]["items"] for doi in doi_dict.values()]
        )
        if len(data["message"]["items"]) < 1000:
            return all_dois
        else:
            cursor = data["message"]["next-cursor"]
            while cursor != "*":
                data = crossref_search(pub_date, query, prefix, pub_type, cursor)
                all_dois.extend(
                    [
                        doi
                        for doi_dict in data["message"]["items"]
                        for doi in doi_dict.values()
                    ]
                )
                if len(data["message"]["items"]) < 1000:
                    return all_dois
                else:
                    cursor = data["message"]["next-cursor"]
