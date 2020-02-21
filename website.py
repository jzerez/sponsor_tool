"""
Spring 2020
Jonathan Zerez

Object that facilitates the graph associated with a specific domain (ex: cimquest-inc.com)
-Performs DFS to find pages in domain
-Extracts email addresses
-Extracts keywords to learn more about the company
"""

from urllib.parse import urlparse
import time
from page import Page
from collections import deque
import pdb
class Website:
    def __init__(self, url, query=None):
        # Main Website Attributes
        self.domain = urlparse(url).netloc
        self.base_url = url
        self.origin_query = query

        self.email_sent = False;

        # adjacency list for the graph of the website
        self.adj_list = {}
        # all links that have been visited
        # a link has been visited if all of its child links have been ackowledged
        self.all_links = set()
        # the set of all emails found in the website
        self.emails = set()
        # a histogram representing the frequency of categories of keywords
        # ex: edu_keywords where found 55 times in the website
        self.hist = {}

    def explore_links(self, queue, max_pages=25):
        """
        Populates the graph of the Website using DFS

        queue: a collections.deque object that contains the first page(s)
               to start searching from
        max_pages: an integer for the novel number of pages to explore
        """

        num_visted = 0
        # while there are children in the queue
        while queue:
            if num_visted >= max_pages:
                break
            # pop the child from queue, explore links
            child_url = queue.popleft()
            # Check to see if the child has already been visited
            if child_url in self.all_links:
                continue
            print('url: ', child_url)
            child_page = Page(child_url, self.domain)


            # once explored, add to adj_list
            adj = self.adj_list.get(child_page.url, [])
            adj.extend(child_page.links)
            self.adj_list[child_page.url] = adj

            # add links to queue
            queue.extend(child_page.links)
            # add url of child to set of visited links
            self.all_links.add(child_page.url)
            self.emails.update(child_page.emails)
            self.combine_hist(child_page.make_text_hist())
            num_visted += 1

    def combine_hist(self, hist):
        """
        Takes the keyword frequency histogram from a Page and adds it to the
        keyword frequency histogram for the Website

        hist: a keyword frequency histogram (dict) from a Page
        """
        for key in hist.keys():
            count = self.hist.get(key, 0) + hist[key]
            self.hist[key] = count


if __name__ == "__main__":
    import time
    site = Website('https://cimquest-inc.com/')
    start = time.time()
    site.explore_links(deque([site.base_url]), max_pages=50)
    print(time.time()-start)
    print(site.all_links)
    print(site.adj_list)
    print(site.emails)
    print(site.hist)
    pdb.set_trace()
