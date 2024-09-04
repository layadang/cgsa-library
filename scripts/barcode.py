# issues with zbar and shared library
# brew zbar
# export DYLD_LIBRARY_PATH="$(brew --prefix)/lib:$DYLD_LIBRARY_PATH"
import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import time

# Sample output for books:
# https://openlibrary.org/books/OL35470544M.json 

# sometimes looks different?
# https://openlibrary.org/works/OL16358673W.json

# Sample output for authors:
# https://openlibrary.org/authors/OL30553A.json 

def get_book_info(isbn):
    url = f"https://openlibrary.org/isbn/{isbn}.json"

    headers = {
        'User-Agent': 'CGSA-library-pd03@bu.edu'
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        title = data.get('full_title', 'None')

        author = ''
        for person in data['authors']:
            url = f"https://openlibrary.org{(person['key'])}.json"
            response = requests.get(url, headers=headers)
            author_data = response.json()
            name = author_data['alternate_names'][0]

            if author == '':
                author = name
            else:
                author += f', {name}'

        return title

    except requests.exceptions.RequestException as e:
        print(f"ISBN not in database, {e}")
        return None

# Art of War testing
get_book_info('9780007420124')

def barcode_scanner():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("camera failed")
            break
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray_frame)
        
        if barcodes:
            barcode = barcodes[0]
            # (x, y, w, h) = barcode.rect
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_data = barcode.data.decode('utf-8')            
            print(f"ISBN: {barcode_data}")
            print(f"Found book: {get_book_info(barcode_data)}")
            time.sleep(0.5)
        
        cv2.imshow('Barcode Scanner', frame)
        
        # press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# barcode_scanner()