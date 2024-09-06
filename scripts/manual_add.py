import pandas as pd
import csv
import os
import requests

from barcode import get_book_info, add_book

# In case books don't have barcodes / barcode.py not reading the scans
# NEED TO ADD: currently only searching ISBN-10, but some books only have ISBN-13 barcodes 

def add_by_isbn():
    entered = input("Enter ISBN or 'q' to quit: ")
    if entered == 'q':
        return False
    title = get_book_info(entered)
    if title is None:
        print("not found :(")
    else: 
        add_book(entered, title)
    return True

# while True:
#     if not add_by_isbn():
#         break 

def add_by_title():
    entered = input("Enter book title here or press 'q' to quit: ")
    if entered == 'q':
        return False 
    
    entered = entered.lower().strip().replace(' ', '+')
    url = f"https://openlibrary.org/search.json?q={entered}"

    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()

    print(data['docs'][0])

    return True

while True:
    if not add_by_title():
        break 