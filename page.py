"""
Spring 2020
Jonathan Zerez

A Page object is responsible for parsing the text and child links in a single
page
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import Request

import pdb

class Page():
    def __init__(self, url, keywords, domain=None):
        self.url = url
        self.tld = urlparse(url).hostname
        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',}
        # set domain
        if domain is None:
            self.domain = urlparse(url).netloc
        else:
            self.domain = domain

        # set of all emails found on the page
        self.emails = set()

        self.request_successful = True
        try:
            # open up the URL
            request = Request(url, None, header)
            response = urlopen(request)
            self.page = BeautifulSoup(response.read(), "lxml")

            # a histogram representing the frequency of categories of keywords
            self.text_hist = self.make_text_hist(keywords)
            # list of all child links that belong to the domain of the site
            self.links = self.find_links()
        except (ValueError, HTTPError) as e:
            print('Warning, the following error was encountered')
            print(e)

            self.request_successful = False
            pass

    def find_links(self):
        """
        Finds all of the links referenced on the page and returns them as a list
        """
        links = []
        for link in self.page.find_all('a'):
            url = link.get('href')
            # Make sure the <a> tag has an href
            if type(url) is not str or not url:
                continue
            if not urlparse(url).scheme:
                try:
                    if url[0] is ':':
                        url = 'https' + url
                    elif url[0] is '/':
                        if url[1] is '/':
                            url = 'https:' + url
                        else:
                            url = 'https:/' + url
                    else:
                        url = 'https:/' + url
                except:
                    continue
            # See if link is an email
            if 'mailto:' in url:

                if url.find('?') == -1:
                    self.emails.add(url.lower())
                else:
                    self.emails.add(url[:url.find('?')].lower())

            # Make sure to reject external links
            elif self.domain in url:

                links.append(url)
        self.explored = True
        return links

    def make_text_hist(self, keywords):
        """
        Gets text of current page, creates and returns histogram based on
        defined keywords
        """
        text_hist = {}
        text = self.page.get_text()
        for word in text.split():
            if word in keywords:
                text_hist[word] = text_hist.get(word, 0) + 1
            if '@' in word and '.'+self.tld in word:
                self.emails.add(word)
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
