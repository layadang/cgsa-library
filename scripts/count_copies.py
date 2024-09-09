import pandas as pd
import csv
import os

copy_dict = {}

# Takes cleaned book info file and counts the number of duplicates
def copy_counter(input_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, input_file)

    isbn_titles = pd.read_csv(file_path)

    isbn_csv = '../data/cleaned_with_count.csv'    # Generate new csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, isbn_csv)
    total = len(isbn_titles.index)

    for i, row in isbn_titles.iterrows():
        curr_isbn = row['isbn']
        if curr_isbn in copy_dict:
            copy_dict[curr_isbn] += 1
        else:
            copy_dict[curr_isbn] = 1

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'isbn', 'numcopies', 'title', 'author', 'genre', 'cover', 'desc', 'collection'])
        for i, row in isbn_titles.iterrows():
            if row['isbn'] in copy_dict:
                writer.writerow([row['id'], row['isbn'], copy_dict[row['isbn']], row['title'], row['author'], row['genre'], row['cover'], row['desc'], row['collection']])
                del copy_dict[row['isbn']]
    print()
    print('Done!')
    return

copy_counter('../data/cleaned_book_info.csv')