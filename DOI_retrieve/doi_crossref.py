"""
Script to retrieve DOIs from Crossref API for specific prefixes
"""
import doi_retrieve_tools as drt
import sys

if __name__ == '__main__':
    pub_dates, query_list, save_dir, _, _, _, _ = drt.parse_args(sys.argv[1:])
    drt.doi_search_crossref(query_list, pub_dates, save_dir)
    drt.doi_unique(query_list, save_dir)