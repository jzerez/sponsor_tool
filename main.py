import webscraper
import website
from sheets import *
from collections import deque
import pprint as pp
import pdb

def init(verbose=False):
    """
    initialize the spreadsheet object and associated supporting data structures
    for a scraping/quering session

    Parameters:
        verbose (bool): toggles progress printing

    Returns:
        spreadsheet (Spreadsheet): the target spreadsheet
        controls (dict): contains the contents of the controls sheet
        blacklist (list): a list of blacklisted domains and company names
        keywords (set): the set of all keywords
        seen_domains (set): a list of domains that have been already been found
                            before and exsist in the domain column of the
                            results worksheet
    """
    spreadsheet = open_spreadsheet()
    if verbose: print('Spreadsheet accessed successfully')

    controls = get_controls(spreadsheet)
    if verbose: print('Controls loaded')

    blacklist = get_blacklist(spreadsheet)
    if verbose: print('Blacklist loaded')

    keywords = get_keywords(spreadsheet)
    if verbose: print('Keywords loaded')

    seen_domains = get_seen_domains(spreadsheet)
    if verbose: print('Seen domains loaded')

    return spreadsheet, controls, blacklist, keywords, seen_domains

def perform_query(spreadsheet, controls, blacklist, seen_domains):
    """
    Performs a google search on a set of queries and stores fetched domains/urls

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet
        controls (dict): contains the contents of the controls sheet
        blacklist (list): a list of blacklisted domains and company names
        seen_domains (set): a list of domains that have been already been found
                            before and exsist in the domain column of the
                            results worksheet

    """
    queries = get_queries_to_search(spreadsheet)
    responses = webscraper.gsearch(queries,
                                   controls['num_queries_per_session'],
                                   controls['num_url_per_query'])
    store_query_responses(spreadsheet, responses, blacklist, seen_domains)

def scrape_sites(spreadsheet, controls, keywords):
    """
    Performs DFS on a series of unexplored sites, store data in results worksheet

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet
        controls (dict): contains the contents of the controls sheet
        keywords (set): the set of all keywords
    """
    website_data = get_website_data_for_scrape(spreadsheet,
                                               controls['num_websites_per_session'])
    for data in website_data:
        domain = data[0]
        base_url = data[1]
        query = data[2]
        row_num = data[3]
        site = website.Website(base_url, domain, query, row_num)
        site.explore_links(deque([site.base_url]), keywords, max_pages=controls['num_pages_per_website'])
        store_scrape_results(spreadsheet, site, controls['auto_email'])

if __name__ == "__main__":
    spreadsheet, controls, blacklist, keywords, seen_domains = init(True)
    if controls['perform_query']:
        print('Performing Query on ', controls['num_queries_per_session'], ' search terms')
        perform_query(spreadsheet, controls, blacklist, seen_domains)
    else:
        print('Skipping Query')

    if controls['perform_scrape']:
        print('Performing scrape on ', controls['num_websites_per_session'], ' websites.')
        print('Each website will have ', controls['num_pages_per_website'], 'pages explored.')
        scrape_sites(spreadsheet, controls, keywords)
    else:
        print('Skipping scrape')
