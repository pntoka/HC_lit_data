'''
Script to retrieve a list of DOIs from semantic scholar based on search query
and publication date
'''
import doi_retrieve_tools as drt
import sys
import os

if __name__ == '__main__':
    pub_dates, query_list, save_dir, pub_type, pub_skip, prefix_list, _ = drt.parse_args(sys.argv[1:])
    drt.doi_search(query_list, pub_dates, save_dir, pub_type=pub_type, pub_skip=pub_skip)
    drt.doi_unique(query_list, save_dir)
    drt.filter_dois(os.path.join(save_dir, 'doi_unique.txt'), prefix_list, save_dir)
