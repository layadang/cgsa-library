import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import time
import pandas as pd
import csv
import os

genre_dict = {}

def get_book_info(isbn):
    url = f"https://openlibrary.org/isbn/{isbn}.json"

    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        # AUTHOR(S)
        author = ''
        if 'authors' in data:
            for person in data['authors']:
                url = f"https://openlibrary.org{(person['key'])}.json"
                response = requests.get(url, headers=headers)
                author_data = response.json()
                name = author_data['name']

                if author == '':
                    author = name
                else:
                    author += f', {name}'
        else:
            author = 'N/A'

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
                if subject in genre_dict:
                    genre_dict[subject] += 1
                else:
                    genre_dict[subject] = 1

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

        return author, genre, cover, desc

    except requests.exceptions.RequestException as e:
        print(f"ISBN not in database, {e}")
        return None

def read_isbn(isbn_csv, start):
    count = 0
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, isbn_csv)

    isbn_titles = pd.read_csv(file_path)

    isbn_csv = '../data/book_info.csv'    # Generate new csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, isbn_csv)
    total = len(isbn_titles.index)

    count = start
    print()
    print(str(count) + "/" + str(total) + " completed.", end="\r")

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if start == 0:
            writer.writerow(['isbn', 'title', 'author', 'genre', 'cover', 'desc'])
        for i, row in isbn_titles.iterrows():
            if i >= start:
                author, genre, cover, desc = get_book_info(row['isbn'])
                i_isbn, i_title = row['isbn'], row['title']
                writer.writerow([i_isbn, i_title, author, genre, cover, desc])
                count += 1
                print(str(count) + "/" + str(total) + " completed.", end="\r")
    print()
    print('Done!')
    return

def process_dict(g_dict, threshold):
    for key in list(g_dict.keys()):
        if g_dict[key] < threshold:
            del g_dict[key]

    genre_csv = '../data/genre_count.csv'    # Generate new csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, genre_csv)

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['genre', 'count'])
        for k in list(g_dict.keys()):
            writer.writerow([k, g_dict[k]])
    
    return g_dict

start_num = int(input("Enter a starting row from isbn-titles.csv: "))
read_isbn('../data/isbn-titles.csv', start_num)


genre_dict = process_dict(genre_dict, 2)
