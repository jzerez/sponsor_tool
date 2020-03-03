"""
Spring, 2020
Jonathan Zerez

This class provides functinoality for querying google for domains that will
later become Website objects
"""

from googlesearch import search
from urllib.parse import urlparse
import pdb
import pprint
# from blacklist import *
# from visited_sites import *
# from queries import *
import time

tld = 'com'
num = 10


try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found. Try running the following commands:")
    print("`pip install beautifulsoup4`")
    print("`pip install google`")


def gsearch(queries, num_url_per_query=10):
    responses = []
    for query, row_num in queries:
        results = search(query, tld=tld, num=num_url_per_query, stop=num_url_per_query, pause=0.5)
        for url in results:
            domain = urlparse(url).netloc
            print(domain)
            response = {}
            response['url'] = url
            response['domain'] = domain
            response['query'] = query
            response['row_num'] = row_num
            responses.append(response)
    return responses
