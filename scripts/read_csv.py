import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import pandas as pd
import csv
import os
import re
from collections import Counter

genre_dict = {}
copy_dict = {}

# words to not capitalize
# remember exceptions for first word and first word after ':' colon
dont = ['the', 'of', 'a', 'an', 'from', 'with', 'for', 'and', 'in', 'at', 'on', 'to', 'for', '\'s']

# key to determine collection based on genre terms

# Collections: Gender Studies, LGBTQ+, Textbooks, Fiction, History, Art, Social Science, Self-help, Other

# Sorted by descending popularity (based on above)
gender = {'women', 'womens', 'feminism', 'gender', 'men', 'mens', 'masculinity', 'sex'}
lgbtq = {'gay', 'homosexuality', 'lesbian', 'orientation', 'sexuality'}
social = {'sociology', 'politics', 'social', 'psychology'}
art = {'art', 'poetry', 'comic'}
fiction = {'fiction'}
history = {'history', 'movement', 'movements'}
self_help = {'selfhelp', 'health'}
textbook = {'textbooks', 'textbook'}

collection = []

def sort_by_collection(genre):
    genre_clean = str(genre).lower()
    genre_clean = re.sub('[^a-zA-Z0-9 ]','', genre_clean)
    genres = (set(genre_clean.split())) # only key words in genre(s)
    
    # each book can only be part of one collection
    # going from least popular to most popular genres in general
    if genres.intersection({"N/A"}):
        col = "other"

    elif genres.intersection(textbook):
        col = "textbook"

    elif genres.intersection(self_help):
        col = "self-help"
    
    elif genres.intersection(history):
        col = "history"

    elif genres.intersection(fiction):
        col = "fiction"

    elif genres.intersection(art):
        col = "art"

    elif genres.intersection(social):
        col = "social science"

    elif genres.intersection(lgbtq):
        col = "lgbtq+"

    elif genres.intersection(gender):
        col = "gender studies"
    
    else:
        col = "other"
    
    collection.append(col)

    return col

def title_case(word, dont):
    """Returns the title-cased version of the word, except for exceptions."""
    if word.lower() in dont:
        return word.lower()
    return word.capitalize()

def clean_title(title):
    follows_colon = False
        
    # Split title into words
    title_words = title.split(" ")
        
    # Capitalize the first word always
    corrected_title = title_words[0].capitalize()
    if (title_words[0].endswith(':')):
        follows_colon = True

    for j, word in enumerate(title_words[1:], start=1):
        if (follows_colon):           # words following colon always capitalized
            corrected_title += " " + word.capitalize()
        else:
            corrected_title += " " + title_case(word, dont)
            
            # Toggle follows_colon based on the presence of a colon
            follows_colon = word.endswith(':')
    # Join list back to string and update info
    return corrected_title

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
                    if name == "n/a":
                        author += f''
                    author += f', {name}'
        else:
            author = ''

        # GENRE
        genre = ''
        subject_data = data.get('subjects', None)
        if subject_data is None:
            genre = ""
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
        col = sort_by_collection(genre)

        # COVER IMAGE (medium)
        cover = ''
        cover += f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

        # DESCRIPTION
        desc = ''
        desc_data = str(data.get('description', None))
        if desc_data is None:
            desc = "No description available."
        else:
            if desc_data.startswith("{'type'"):
                #desc_data = str(eval(desc_data)['value'])
                desc_data = desc_data[32:-3]
            if (desc_data == "None"):
                desc_data = "No description available."
            desc = desc_data

        return author, genre, cover, desc, col

    except requests.exceptions.RequestException as e:
        print(f"ISBN not in database, {e}")
        return None

def read_isbn(isbn_csv, start):
    count = 0
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, isbn_csv)

    isbn_titles = pd.read_csv(file_path)

    isbn_csv = '../data/book_info_w_man.csv'    # Generate new csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, isbn_csv)
    total = len(isbn_titles.index)

    for i, row in isbn_titles.iterrows():
        curr_isbn = row['isbn']
        if curr_isbn in copy_dict:
            copy_dict[curr_isbn] += 1
        else:
            copy_dict[curr_isbn] = 1

    count = start
    print()
    print(str(count) + "/" + str(total) + " completed.", end="\r")

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if start == 0:
            writer.writerow(['id', 'isbn', 'numcopies', 'title', 'author', 'genre', 'cover', 'desc', 'collection'])
        for i, row in isbn_titles.iterrows():
            if (i >= start) and (row['isbn'] in copy_dict):
                author, genre, cover, desc, col = get_book_info(row['isbn'])
                i_isbn, i_title = row['isbn'], clean_title(row['title'])
                writer.writerow([i, i_isbn, copy_dict[curr_isbn], i_title, author, genre, cover, desc, col])
                count += 1
                del copy_dict[row['isbn']]
                print(str(count) + "/" + str(total) + " completed.", end="\r")
    print()
    print('Done!')
    return

def remove_nones(cleaned_csv):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, cleaned_csv)

    info = pd.read_csv(file_path)

    for i, row in info.iterrows():
        if str(row['desc']).startswith("{'type'"):
            new_desc = str(eval(row['desc'])['value'])
            info.at[i, 'desc'] = new_desc # directly update df


def process_dict(g_dict, threshold):

    genre_csv = '../data/genre_count_w_man.csv'    # Generate new csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, genre_csv)

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['genre', 'count'])
        for k in list(g_dict.keys()):
            if g_dict[k] >= threshold:
                writer.writerow([k, g_dict[k]])
    
    return g_dict

start_num = int(input("Enter a starting row from isbn-titles.csv (enter 0 to start from beginning): "))
read_isbn('../data/isbn-titles.csv', start_num)


genre_dict = process_dict(genre_dict, 2)