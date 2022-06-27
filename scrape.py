import os
import re
import pandas as pd
import random
import time
import json
import datetime
from pprint import pprint
from requests_html import HTMLSession
from urllib.parse import quote_plus
from timeout import timeout

def user_params():
    """Initialize the scraper by checking a JSON file.
    """
    json_file = os.path.join(os.getcwd(), 'params.json')
    with open(json_file) as file:
        data = json.load(file)
        filename = data['filename']
        colname = data['colname']
        regex = data['regex']
        term_list_2 = data['terms']
        css = data['css']
    
    if not os.path.exists(filename):
        print("The csv file doesn't exist in this directory.")
        return
    
    try:
        term_list_1 = pd.read_csv(filename)[colname]
    except KeyError:
        print(f"Column {colname} not found in {filename}.")
        return
    print(f"Initializing gscraper for {len(term_list_1)} rows in {filename} and searching for {term_list_2}")

    return filename, colname, regex, term_list_1, term_list_2, css


@timeout(20)
def search(query):
    """Send a GET request to Google's search engine with a query.
    Args: 
        query (string) - String value that is escaped and encoded and passed to Google's search
    
    Returns:
        response (requests.Response)
    """
    session = HTMLSession()
    response = session.request(
                'GET',
                "https://www.google.com/search?q=" + quote_plus(query),
                headers = {
                    "user-agent" : 
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
                    })
    return response


@timeout(20)
def parse(response, result_class, filter, filter_url=True):
    """Parse a requests.Response object and returns a filtered list of dictionaries

    Args:
        response (requests.Response) - HTTP response object from Google's search
        result_class (string) - Class selector of Google's result, eg ".yuRUbf"
        filter (string) - Regex string to be compiled and matched against
        filter_url (bool) - Switch to decide what to filter on. By default, will filter by URL; else will filter by search result title.

    Returns:
        output ([dict])
    """
    css_title = "h3"
    css_link = "a"
    
    results = response.html.find(result_class)

    output = []
    for result in results:
        item = {
            'title': result.find(css_title, first=True).text,
            'link': result.find(css_link, first=True).attrs['href']
        }
        if filter_url == False:
            if filter.match(item['title']):
                output.append(item)
        else: 
            if filter.match(item['link']):
                output.append(item)
        
    return output


def google_search():
    """Calls user_params, search, and parse to produce a dataframe which
    represent the full output of the search.

    Returns:
        df (pd.Dataframe)
    """
    list_of_dicts = []
    try:
        filename, colname, regex, term_list_1, term_list_2, css = user_params()
    except:
        print("Execution failed. Kindly rerun the script with the correct parameters.")
        return
    
    for term1 in term_list_1:
        try:
            for term2 in term_list_2:
                r = search(term1 + ' ' + term2)
                
                # Exit if blocked by Google
                if r.status_code == 429:
                    print("Search returned error: {r.status_code} {r.reason} for {term1} {term2}. Terminating loop.")
                    break 

                output = parse(r, css, re.compile(regex))
                for el in output:
                    el[colname] = term1
                    el['query'] = term2
                    list_of_dicts.append(el)
                    print(r.status_code, r.reason)
                    pprint(el)
                time.sleep(random.randint(30, 45))
                continue
        except:
            break
    
    df = pd.DataFrame(list_of_dicts)
    print(df.head())
    o_filename = filename.split('.')[0] + '-output_' + str(datetime.datetime.now()) + '.csv'
    df.to_csv(o_filename, index=False)
    return df

if __name__ == '__main__':
    google_search()
    
