"""
Summer, 2019
This file provides functionality for google search abilities. As of Spring 2020,
this script is depreciated. Use the google python package instead, as it doesn't
require an API secret or a CSE id. New google search functionality built into
#TODO
"""

import os.path
import pdb
from googleapiclient.discovery import build

def get_keys(api_file='api_secret.txt', cse_file='cse_id.txt'):
    assert os.path.isfile(api_file), 'API key missing!'
    assert os.path.isfile(cse_file), 'CSE ID missing!'

    api_secret = open('api_secret.txt', 'r').read().strip()
    cse_id = open('cse_id.txt', 'r').read().strip()
    return api_secret, cse_id

def google_search(term, api_key, cse_id, num=10):
    service = build('customsearch', 'v1', developerKey=api_key)
    res = service.cse().list(q=term, cx=cse_id, num=num).execute()
    pdb.set_trace()
    return parse_response(res['items'], term)

def parse_response(response, term):
    links = []
    for i,link in enumerate(response):
        pdb.set_trace()
        links.append({'title': link['title'], 'description': link['snippet'], 'domain': link['displayLink'], 'url': link['link'], 'query':term})
    return links

if __name__ == "__main__":
    api_secret, cse_id = get_keys()
    from sample_response import response
    import pprint
    l = parse_response(response, 'so')
    print('previous query')
    pprint.pprint(l)


    results = google_search(
        'fabrication services near me', api_secret, cse_id, 2)
    for result in results:
        pprint.pprint(result)
    pprint.pprint(results)
    print(len(results))
