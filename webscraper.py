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
from blacklist import *
from visited_sites import *
from queries import *
import time

tld = 'com'
num = 10


try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found. Try running the following commands:")
    print("`pip install beautifulsoup4`")
    print("`pip install google`")

domains = set()

for query in queries:
    responses = search(query, tld=tld, num=num, stop=num, pause=2)
    for response in responses:
        domains.add(response)
        time.sleep(1)
    break

print(domains)
