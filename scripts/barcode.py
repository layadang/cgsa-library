# issues with zbar and shared library
# brew zbar
# export DYLD_LIBRARY_PATH="$(brew --prefix)/lib:$DYLD_LIBRARY_PATH"
import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import time
import pandas as pd
import csv
import os

# Sample output for books:
# https://openlibrary.org/books/OL35470544M.json 

# sometimes looks different?
# https://openlibrary.org/works/OL16358673W.json

# Sample output for authors:
# https://openlibrary.org/authors/OL30553A.json 

### GETS BOOK TITLE FROM OPEN LIBRARY API
def get_book_info(isbn):

    # API url 
    url = f"https://openlibrary.org/isbn/{isbn}.json"

    # Developer information per open library policy
    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        # if full_title index exists
        title = data.get('full_title', None)

        # then there is probably title
        if title is None:
            title = data.get('title', None)

        # in case there's a second path
        subtitle = data.get('subtitle', None)
        if subtitle:
            title += ': ' + subtitle

        return title

    except requests.exceptions.RequestException as e:
        print(f"ISBN not in database, {e}")
        return None

### ADDS BOOK ISBN AND TITLE TO A CSV

# path to csv that stores isbn and title info
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '../data/isbn-titles.csv')

# initialize lists for function
all_isbn = []
all_titles = []
# to make sure there are no duplicates
pre_isbn = pd.read_csv(file_path)['isbn'].tolist() 

def add_book(isbn, title):
    confirmation = input(f"Enter 1 to add book '{title}': ")

    # user must manually confirm title matches, book must also not already be in database
    if (confirmation == '1') and (isbn not in pre_isbn):
        all_isbn.append(isbn)
        pre_isbn.append(isbn)
        all_titles.append(title)

        # append new book to csv
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([isbn, title])
            print('Added!')
###

### "BARCODE SCANNER" USING WEBCAM / main function
def barcode_scanner():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("camera failed")
            break
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # # from: https://stackoverflow.com/questions/50080949/qr-code-detection-from-pyzbar-with-camera-image
        # mask = cv2.inRange(frame,(0,0,0),(200,200,200))
        # thresholded = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
        # gray_frame = 255-thresholded
        barcodes = decode(gray_frame)
        
        if barcodes:
            barcode = barcodes[0]
            # (x, y, w, h) = barcode.rect
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_data = barcode.data.decode('utf-8')    
            title = get_book_info(barcode_data)        
            print(f"ISBN: {barcode_data}")
            print(f"Found book: {title}")

            if title is not None:
                add_book(barcode_data, title)

            time.sleep(0.2)
        
        cv2.imshow('Barcode Scanner', frame)
        
        # press 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
###

# calling main function
if __name__ == "__main__":
    barcode_scanner()