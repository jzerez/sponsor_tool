"""
Spring 2020
Jonathan Zerez

A Page object is responsible for parsing the text and child links in a single
page
"""

from bs4 import BeautifulSoup
import urllib
import pdb
import keywords

class Page():
    def __init__(self, url, domain=None):
        self.url = url
        
        # set domain
        if domain is None:
            self.domain = urllib.urlparse(url).netloc
        else:
            self.domain = domain

        # open up the URL
        response = urllib.request.urlopen(url)
        self.page = BeautifulSoup(response.read(), "lxml")



        # set of all emails found on the page
        self.emails = set()
        # a histogram representing the frequency of categories of keywords
        # ex: edu_keywords where found 55 times in the website
        self.text_hist = self.make_text_hist()
        # list of all child links that belong to the domain of the site
        self.links = self.find_links()


    def find_links(self):
        """
        Finds all of the links referenced on the page and returns them as a list
        """
        links = []
        for link in self.page.find_all('a'):
            url = link.get('href')
            # Make sure the <a> tag has an href
            if type(url) is not str:
                continue
            # See if link is an email
            if 'mailto:' in url:
                self.emails.add(url)

            # Make sure to reject external links
            elif self.domain in url:
                links.append(url)
        self.explored = True
        return links

    def make_text_hist(self):
        """
        Gets text of current page, creates and returns histogram based on
        defined keywords
        """
        text_hist = {}
        text = self.page.get_text()
        for word in text.split():
            if word in keywords.keywords.keys():
                category = keywords.keywords[word]
                text_hist[category] = text_hist.get(category, 0) + 1

        return text_hist

if __name__ == "__main__":
    print(keywords.c2)
    # n = Node("https://cimquest-inc.com/");
    # neigh = n.find_links()
    #
    # print(len(neigh))
    # print(type(neigh))
    # print(n.domain)
    # print(n.emails)
