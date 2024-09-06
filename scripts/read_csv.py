import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import time
import pandas as pd
import csv
import os

def get_book_info(isbn):
    url = f"https://openlibrary.org/isbn/{isbn}.json"

    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        title = data.get('full_title', None)
        
        # TITLE, SUBTITLE
        if title is None:
            title = data.get('title', None)

        subtitle = data.get('subtitle', None)
        if subtitle:
            title += ': ' + subtitle

        # AUTHOR(S)
        author = ''
        for person in data['authors']:
            url = f"https://openlibrary.org{(person['key'])}.json"
            response = requests.get(url, headers=headers)
            author_data = response.json()
            name = author_data['name']

            if author == '':
                author = name
            else:
                author += f', {name}'

        # GENRE
        genre = ''
        subject_data = data.get('subjects', None)
        if subject_data is None:
            genre = "N/A"
        else:
            for subject in subject_data:
                if genre == '':
                    genre = subject
                else:
                    genre += f', {subject}'

        # COVER IMAGE (medium)
        cover = ''
        cover += f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

        # DESCRIPTION
        desc = ''
        desc_data = data.get('description', None)
        if desc_data is None:
            desc = "N/A"
        else:
            desc = desc_data
        
        # CSV
        isbn_csv = '../data/' + str(isbn) + '.csv'    # Generate new csv
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, isbn_csv)

        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for item in [title, author, genre, cover, desc]:
                writer.writerow([item])
            print('Added!')

        return title

    except requests.exceptions.RequestException as e:
        print(f"ISBN not in database, {e}")
        return None
    
get_book_info(9780679434597)