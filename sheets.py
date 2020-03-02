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
    Accesses the spreadsheet using credentials in client_secret.json, and
    returns the spreadsheet object
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    assert os.path.isfile(creds_file), "API private authentication missing."
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open(name)
    return spreadsheet

def get_controls(spreadsheet):
    sheet = spreadsheet.worksheet("Control")
    cell_values = sheet.col_values(2)
    controls = {}
    controls['num_url_per_query'] = int(cell_values[0])
    controls['auto_email'] = cell_values[1]=="Yes"
    controls['num_queries_per_session'] = int(cell_values[2])
    controls['num_websites_per_session'] = int(cell_values[3])
    controls['num_pages_per_website'] = int(cell_values[4])
    controls['perform_query'] = cell_values[5]=="Yes"
    controls['perform_scrape'] = cell_values[6]=="Yes"
    return controls

def get_queries_sheet(spreadsheet):
    return spreadsheet.worksheet("Queries")

def get_blacklist_sheet(spreadsheet):
    return spreadsheet.worksheet("Blacklist")

def get_keywords_sheet(spreadsheet):
    return spreadsheet.worksheet("Keywords")

def get_results_sheet(spreadsheet):
    return spreadsheet.worksheet("Results")

def get_queries_to_search(spreadsheet):
    """
    returns a list of tuples containing queries and corresponding row numbers
    for queries that have yet to be searched. A query is flagged for searching
    if the corresponding date cell is empty, or has value NULL
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

    for query, date, row_num in zip(all_queries, dates, range(HEADER_OFFSET+1, last_row+1)):
        if not date.value or date.value.lower()=='null':
            queries_to_search.append((query, row_num))
    return queries_to_search

def store_query_responses(spreadsheet, responses, blacklist, seen_domains):
    query_sheet = get_queries_sheet(spreadsheet)
    results_sheet = get_results_sheet(spreadsheet)
    first_empty_row = get_last_row(results_sheet, 1) + 1
    queries_updated = set()

    for response in responses:
        valid = True
        if response['query'] not in queries_updated:
            query_sheet.update_cell(response['row_num'], 2, str(date.today()))
            queries_updated.add(response['query'])
        domain = response['domain']
        for item in blacklist:
            if item.lower() in domain.lower():
                valid = False
                break
        if domain in seen_domains:

            valid = False

        if valid:
            results_sheet.update_cell(first_empty_row, 1, response['domain'])
            results_sheet.update_cell(first_empty_row, 2, response['url'])
            results_sheet.update_cell(first_empty_row, 3, response['query'])
            results_sheet.update_cell(first_empty_row, 4, 'No')
            first_empty_row += 1
            seen_domains.add(domain)

def list_into_cell(cell, terms):
    """
    takes a list of strings and appends them as comma separated values to a cell
    with a specified row and col number
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
    return the row number of the last populated row in the column
    """
    all_cols = sheet.col_values(col)
    return len(all_cols)

def get_seen_domains(spreadsheet):
    sheet = get_results_sheet(spreadsheet)
    return set(sheet.col_values(1)[HEADER_OFFSET:])

def get_blacklist(spreadsheet):
    sheet = get_blacklist_sheet(spreadsheet)
    return sheet.col_values(1)[1:]

def get_website_data_for_scrape(spreadsheet, num_websites_per_session):
    sheet = get_results_sheet(spreadsheet)
    searched_row = sheet.col_values(4)[1:]
    inds = []
    for row, was_searched in enumerate(searched_row):
        if row >= num_websites_per_session:
            break
        if was_searched=="No": inds.append(row+2)

    website_data = []
    for ind in inds:
        target_cell_range = "A"+str(ind)+":"+"C"+str(ind)
        cell_list = sheet.range(target_cell_range)
        values = tuple([cell.value for cell in cell_list] + [ind])
        website_data.append(values)
    return website_data

def get_keywords(spreadsheet):
    sheet = get_keywords_sheet(spreadsheet)
    edu_keywords = sheet.col_values(1)[HEADER_OFFSET:]
    elec_keywords = sheet.col_values(2)[HEADER_OFFSET:]
    mech_keywords = sheet.col_values(3)[HEADER_OFFSET:]
    return set(edu_keywords + elec_keywords + mech_keywords)

def store_scrape_results(spreadsheet, website, auto_email):
    sheet = get_results_sheet(spreadsheet)
    assert website.explored
    row_num = website.row_num
    target_cell_range = "D"+str(row_num)+":"+"J"+str(row_num)
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
    # cell_list[1].value



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
