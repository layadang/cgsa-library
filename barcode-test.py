import cv2
import pyzbar.pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
import requests

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
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            barcode_data = barcode.data.decode('utf-8')            
            print(f"ISBN: {barcode_data}")
            break
        
        cv2.imshow('Barcode Scanner', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # cap.release()
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    barcode_scanner()