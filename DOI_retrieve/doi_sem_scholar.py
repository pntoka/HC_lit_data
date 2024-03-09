'''
Script to retrieve a list of DOIs from semantic scholar based on search query
and publication date
'''
import doi_retrieve_tools as drt
import sys
import os

if __name__ == '__main__':
    pub_dates, query_list, save_dir = drt.parse_args(sys.argv[1:])
    drt.doi_search(query_list, pub_dates, save_dir)
    drt.doi_unique(query_list, save_dir)
    prefixes = [
        '10.1016',
        '10.1021',
        '10.1039',
        '10.1002',
        '10.1007',
        '10.1080',
        '10.1038'
    ]
    drt.filter_dois(os.path.join(save_dir, 'doi_unique.txt'), prefixes, save_dir)
