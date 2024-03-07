from DOI_retrieve.doi_retrieve_tools import parse_query
import os


p = os.path.dirname(__file__)


def test_parse_query_dates():
    correct_pd = [2010, 2011, 2012, 2013, 2014]
    correct_sq = [
        'hard carbon sodium ion battery',
        'non-graphite carbon materials'
    ]
    pub_dates, search_queries = parse_query(os.path.join(p, 'query_test.txt'))
    assert pub_dates == correct_pd and search_queries == correct_sq
