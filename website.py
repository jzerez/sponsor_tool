"""
Spring 2020
Jonathan Zerez

Object that facilitates the graph associated with a specific domain (ex: cimquest-inc.com)
-Performs BFS to find pages in domain
-Extracts email addresses
-Extracts keywords to learn more about the company
"""

from urllib.parse import urlparse
import time
from page import Page
from collections import deque
import pdb
class Website:
    def __init__(self, url, domain=None, query=None, row_num=None):
        # Main Website Attributes
        if not domain:
            self.domain = urlparse(url).netloc
        else:
            self.domain = domain

        self.base_url = url
        self.origin_query = query
        self.row_num = row_num

        self.explored = False;

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
        self.location = None

    def explore_links(self, queue, keywords, max_pages=25):
        """
        Populates the graph of the Website using BFS

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
            if child_url==self.base_url or child_url==self.domain or 'contact' in child_url:
                use_selenium = True
            else:
                use_selenium = False
            child_page = Page(child_url, keywords, self.domain, use_selenium=use_selenium)

            if not child_page.request_successful:
                continue

            # once explored, add to adj_list
            adj = self.adj_list.get(child_page.url, [])
            adj.extend(child_page.links)
            self.adj_list[child_page.url] = adj

            priority_links, other_links = child_page.filter_links()
            # add links to queue
            queue.extend(other_links)
            queue.extendleft(priority_links[::-1])

            # add url of child to set of visited links
            self.all_links.add(child_page.url)
            self.emails.update(child_page.emails)
            self.combine_hist(child_page.text_hist)
            num_visted += 1
        self.explored = True

    def combine_hist(self, hist):
        """
        Takes the keyword frequency histogram from a Page and adds it to the
        keyword frequency histogram for the Website

        hist: a keyword frequency histogram (dict) from a Page
        """
        for key in hist.keys():
            count = self.hist.get(key, 0) + hist[key]
            self.hist[key] = count

    def get_top_keywords(self, num=3):
        top_items = sorted(self.hist.items(), key=lambda x: x[1])
        if len(top_items) > num:
            top_items = top_items[:num]
        if not top_items:
            return None
        else:
            return [i[0] for i in top_items]

if __name__ == "__main__":
    import time
    site = Website('https://www.atprecision.com/cnc-machine-shop-serving/boston-massachusetts-machining.php')
    site.explore_links(deque([site.base_url]), ['circuit'])
    print(site.emails)
