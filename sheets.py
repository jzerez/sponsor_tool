"""
Jonathan Zerez
Spring 2020

This script provides functionality for reading and writing to google sheets,
allowing users to interact with the sponsorship bot
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint as pp
import os
from datetime import date
import pdb

HEADER_OFFSET = 1

def open_spreadsheet(name="Sponsorship Bot", creds_file='creds/client_secret.json'):
    """
    Accesses the specified spreadsheet using provided credentials

    Parameters:
        name (string): The name of the spreadsheet to access
        creds_file (string): The file path for the json file that contains the
                         credentials for the google drive API

    Returns:
        spreadsheet (Spreadsheet): a Spreadsheet object

    Note:
        The email associated with the service account that accesses and edits
        the spreadsheet needs to be given editing priviledges. This can be done
        by sharing the spreadsheet to the associated email using the normal
        google sheets GUI
    """
    # credentials are needed for both google drive API and google sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # ensure credential file exsists in the /creds folder
    assert os.path.isfile(creds_file), "API private authentication missing."
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)

    # Load the spreadsheet with specified name
    spreadsheet = client.open(name)
    return spreadsheet

def get_queries_sheet(spreadsheet):
    return spreadsheet.worksheet("Queries")

def get_blacklist_sheet(spreadsheet):
    return spreadsheet.worksheet("Blacklist")

def get_keywords_sheet(spreadsheet):
    return spreadsheet.worksheet("Keywords")

def get_results_sheet(spreadsheet):
    return spreadsheet.worksheet("Results")

def get_controls(spreadsheet):
    """
    Get control variables from the controls worksheet of the spreadsheet

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet

    Returns:
        controls (dict): that contains the contents of the controls sheet
    """
    sheet = spreadsheet.worksheet("Control")
    cell_values = sheet.col_values(2)
    controls = {}
    # Populate the dictionary according to the cells from the spreadsheet
    controls['num_url_per_query'] = int(cell_values[0])
    controls['auto_email'] = cell_values[1]=="Yes"
    controls['num_queries_per_session'] = int(cell_values[2])
    controls['num_websites_per_session'] = int(cell_values[3])
    controls['num_pages_per_website'] = int(cell_values[4])
    controls['perform_query'] = cell_values[5]=="Yes"
    controls['perform_scrape'] = cell_values[6]=="Yes"
    return controls

def get_seen_domains(spreadsheet):
    """
    Gets domains that have been added to the results worksheet

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet

    Returns:
        (set): a set of strings of the seen domains
    """
    sheet = get_results_sheet(spreadsheet)
    return set(sheet.col_values(1)[HEADER_OFFSET:])

def get_blacklist(spreadsheet):
    """
    Gets the blacklisted domains/comanies from the blacklist worksheet

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet

    Returns:
        (list): a list of the blacklisted terms
    """
    sheet = get_blacklist_sheet(spreadsheet)
    return sheet.col_values(1)[1:]

def get_keywords(spreadsheet):
    """
    Gets the keywords stored in the keywords worksheet

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet

    Returns:
        (set): the set of all keywords in the keywords worksheet

    Note:
        No distinction is made between educational, mechanical, and electrical
        keywords
    """
    sheet = get_keywords_sheet(spreadsheet)
    edu_keywords = sheet.col_values(1)[HEADER_OFFSET:]
    elec_keywords = sheet.col_values(2)[HEADER_OFFSET:]
    mech_keywords = sheet.col_values(3)[HEADER_OFFSET:]
    return set(edu_keywords + elec_keywords + mech_keywords)

def list_into_cell(cell, terms):
    """
    Takes a list of strings and creates a single string of comma separated
    values. Will append to the contents of a cell if it has exsisting data

    Parameters:
        cell (Cell): the cell to write to
        terms (list): list of strings to concatenate

    Returns
        new_string (string): the new comma separated string
    """

    if cell.value:
        new_string = cell.value + ", " + terms[0]
    else:
        new_string = terms[0]
    for term in terms[1:]:
        new_string += ", " + term
    return new_string

def get_last_row(sheet, col):
    """
    Retrieve the last populated row of a column

    Parameters:
        sheet (Sheet): the target sheet
        col (int): the integer representing the target column number

    Returns:
        (int): the (spreadsheet) index of the last populated row

    Note:
        follows spreadsheet indexing: starts at 1
    """
    all_cols = sheet.col_values(col)
    return len(all_cols)

def get_queries_to_search(spreadsheet):
    """
    Fetches queries that have yet to  be searched

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet

    Returns:
        queries_to_search (list): A list of tuples containing queries that have
                                  yet to be searched and corresponding row
                                  numbers from the queries sheet
    Note:
        A query is flagged for searching if the corresponding date cell is empty
        or has value NULL
    """
    # Sheet 1 is the queries sheet
    sheet = get_queries_sheet(spreadsheet)

    # Gather all queries, skipping the header rows 1-3
    all_queries = sheet.col_values(1)[HEADER_OFFSET:]
    # The row number of the last query
    last_row = get_last_row(sheet, 1)
    # Get the date cells corresponding to the queries
    dates = sheet.range('B2:B'+str(last_row))
    queries_to_search = []
    # the row numbers of all the cells other than the header
    row_nums = range(HEADER_OFFSET+1, last_row+1)

    for query, date, row_num in zip(all_queries, dates, row_nums):
        if not date.value or date.value.lower()=='null':
            queries_to_search.append((query, row_num))
    return queries_to_search

def store_query_responses(spreadsheet, responses, blacklist, seen_domains):
    """
    Saves responses (URLs and domains) from queries in the queries sheet and
    results sheets

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet
        responses (list): a list of dicts generated by gsearch() from
                          webscraper.py
        blacklist (list): a list of blacklisted domains and company names
        seen_domains (set): a list of domains that have been already been found
                            before and exsist in the domain column of the
                            results worksheet
    """
    query_sheet = get_queries_sheet(spreadsheet)
    results_sheet = get_results_sheet(spreadsheet)
    # get the first empty row from the results sheet for writing data
    first_empty_row = get_last_row(results_sheet, 1) + 1
    queries_updated = set()

    for response in responses:
        valid = True
        # Only update the query date cell once, and not once for each response
        if response['query'] not in queries_updated:
            query_sheet.update_cell(response['row_num'], 2, str(date.today()))
            queries_updated.add(response['query'])
        domain = response['domain']
        # Make sure a blacklisted work is not in the domain
        for item in blacklist:
            if item.lower() in domain.lower():
                valid = False
                break
        # Make sure the domain isn't a part of the set of seen domains
        if domain in seen_domains:
            valid = False

        # If the domain is unique and not blacklisted, add it to the results
        # sheet
        if valid:
            results_sheet.update_cell(first_empty_row, 1, response['domain'])
            results_sheet.update_cell(first_empty_row, 2, response['url'])
            results_sheet.update_cell(first_empty_row, 3, response['query'])
            results_sheet.update_cell(first_empty_row, 4, 'No')
            first_empty_row += 1
            seen_domains.add(domain)

def get_website_data_for_scrape(spreadsheet, num_websites_per_session):
    """
    Collects website data (base url, domain, query, and row number in the
    results sheet) for domains that have yet to be queried

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet
        num_websites_per_session (int): the number of websites to scrape

    Returns:
        website_data (list): list of tuples containing the website data

    Note:
        The tuple has the following form
            (Domain, Original URL, Query, row number)
    """
    sheet = get_results_sheet(spreadsheet)
    # find all of the domains that have not been flagged as searched
    searched_row = sheet.col_values(4)[1:]
    inds = []
    for row, was_searched in enumerate(searched_row):
        if row >= num_websites_per_session:
            break
        if was_searched=="No": inds.append(row+2)

    website_data = []
    for ind in inds:
        # get the appropriate cells A-C
        # this corresponds to: (domain, original url, query)
        target_cell_range = "A"+str(ind)+":"+"C"+str(ind)
        cell_list = sheet.range(target_cell_range)
        values = tuple([cell.value for cell in cell_list] + [ind])
        website_data.append(values)
    return website_data

def store_scrape_results(spreadsheet, website, auto_email):
    """
    Populate columns D-J of the results worksheet with the data of a scraped
    website

    Parameters:
        spreadsheet (Spreadsheet): the target spreadsheet
        website (Website): the scraped website
        auto_email (bool): a control bool for whether emails should be sent
                           automatically
    """
    sheet = get_results_sheet(spreadsheet)
    # ensure that the website has been explored
    # ie: website.explore_links() has been called
    assert website.explored
    row_num = website.row_num
    target_cell_range = "D"+str(row_num)+":"+"J"+str(row_num)
    # get associated cells
    cell_list = sheet.range(target_cell_range)

    # Set 'Searched' field to "Yes"
    cell_list[0].value = "Yes"

    # Get the top keywords and populate field
    top_keywords = website.get_top_keywords()
    if top_keywords:
        cell_list[1].value = list_into_cell(cell_list[1], top_keywords)
    else:
        cell_list[1].value = 'NO KEYWORDS FOUND'

    # Location information
    cell_list[2].value = website.location

    # Email information
    if website.emails:
        cell_list[3].value = list_into_cell(cell_list[3], list(website.emails))
    else:
        cell_list[3].value = 'NO EMAILS FOUND'

    # Email sending and autorization information
    if auto_email:
        cell_list[4].value = "Yes"
        cell_list[5].value = "Yes"
    else:
        cell_list[4].value = "No"
        cell_list[5].value = "No"
    sheet.update_cells(cell_list)




if __name__ == "__main__":
    s = open_spreadsheet()
    # qs = get_queries_to_search(s)
    # import webscraper
    # resps = webscraper.scrape(qs, 2, 10)
    # pp.pprint(resps)
    # blacklist = get_blacklist(s)
    # seen_domains = get_seen_domains(s)
    # store_query_responses(s, resps, blacklist, seen_domains)
    print(get_website_info_for_scrape(s, 3))
