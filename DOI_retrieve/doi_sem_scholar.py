'''
Script to retrieve a list of DOIs from semantic scholar based on search query and publication date
'''
import doi_retrieve_tools
import sys

if __name__ == '__main__':
    pub_dates, query_list, save_dir = doi_retrieve_tools.parse_args(sys.argv[1:])
    query_list = ['carbon dots hydrothermal synthesis', 'carbon dots solvothermal synthesis',
                  'carbon quantum dots hydrothermal synthesis', 'carbon nanodots hydrothermal syntehsis',
                  'graphene quantum dots hydrothermal synthesis', 'carbon polymer dots hydrothermal synthesis']
    save_dir = '/Users/pnt17/Library/CloudStorage/OneDrive-ImperialCollegeLondon/MRes_project_data/doi_sem_scholar_2/'
    pub_dates = list(range(2005,2024,1))
    doi_retrieve_tools.doi_search(query_list[4:], pub_dates, save_dir)
    doi_retrieve_tools.doi_unique(query_list, pub_dates, save_dir) 