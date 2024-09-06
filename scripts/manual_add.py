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

# ADDING BY ENTERING TITLE BC THESE BOOKS DON'T HAVE BARCODES
# separate file bc we might print barcode onto them
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '../data/manual-isbn-titles.csv')

def add_by_title():
    entered = input("Enter book title here or press 'q' to quit: ")
    if entered == 'q':
        return False 
    
    entered = entered.lower().strip().replace(' ', '+')
    url = f"https://openlibrary.org/search.json?q={entered}"
    print(url)
    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()

    # get first result from search

    if data['numFound'] != 0:
        # list of all isbn for books - only taking the first one that has isbn and title
        isbn = data['docs'][0]['isbn'][0]
        title = (data['docs'][0]['title'])

        # confirm book is added
        confirmation = input(f"Press 1 to add book '{title}' with ISBN {isbn}: ")

        if (confirmation == '1'):
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([isbn, title])
                print('Added!')
    else:
        print('book not found')

    return True

while True:
    if not add_by_title():
        break 