import os


def read_doi_file(path):
    with open(path, 'r') as f:
        dois = f.readlines()
    doi_list = [doi.strip() for doi in dois]
    return doi_list


def make_batches(doi_list, batch_size=50):
    batches = [doi_list[i:i+batch_size] for i in range(0, len(doi_list), batch_size)]
    return batches