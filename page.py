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
from urllib.error import URLError
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from socket import timeout

import pdb

class Page():
    def __init__(self, url, keywords, domain=None, use_selenium=False):
        self.url = url
        self.tld = urlparse(url).hostname

        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}
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
            response = urlopen(request, timeout=10)
            self.page = BeautifulSoup(response.read(), "lxml")

            # a histogram representing the frequency of categories of keywords
            self.text_hist = self.make_text_hist(keywords)
            # list of all child links that belong to the domain of the site
            self.links = self.find_links(use_selenium)
        except (ValueError, HTTPError, URLError) as e:
            print('Warning, the following error was encountered')
            print(e)

            self.request_successful = False
            pass
        except timeout:
            print('Request timed out')
            self.request_successful = False
            pass

    def find_links(self, use_selenium=True):
        """
        Finds all of the links referenced on the page and returns them as a list
        """
        links = self.find_links_html()
        if use_selenium:
            emails = self.find_emails_selenium()
            self.emails.update(emails)
        return links

    def find_links_html(self):
        """
        Finds all of the links referenced on the page and returns them as a list
        simply uses the html recieved from urlopen to look for links
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

    def find_emails_selenium(self):
        """
        Opens the page using selenium webdriver, and subsequently fetches emails
        """
        # Initialize the driver
        chrome_path = r"/usr/bin/chromedriver"
        driver = webdriver.Chrome(chrome_path)
        driver.set_page_load_timeout(15)
        try:
            driver.get(self.url)
        except TimeoutException as ex:
            print('selenium chromedriver timeout :()')
            driver.close()
            return []

        # wait for site to load assets
        import time
        time.sleep(1)

        # get all hrefs from all <a> tags in the page
        links = driver.find_elements_by_xpath("//a")
        hrefs = [link.get_attribute("href") for link in links]


        # get emails from hrefs
        emails = [href for href in hrefs if href and "mailto:" in href]

        return emails

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

    def filter_links(self, keywords=['contact', 'contact-us']):
        priority_links = []
        other_links = []

        for link in self.links:
            added=False
            for keyword in keywords:
                if keyword in link.lower():
                    priority_links.append(link)
                    added = True
                    break
            if not added:
                other_links.append(link)
        priority_links.sort(key=lambda x: len(x))
        return priority_links, other_links


if __name__ == "__main__":
    p = Page('https://www.python.org', ['lmao'], use_selenium=False)
    p = Page('https://www.seamless.com/food/margaritas_mexican_restaurant/ma-wellesley', ['lmao'], use_selenium=False)

    print(p.emails)
