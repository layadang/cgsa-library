# terminal run $ flask --app app --debug run
from flask import Flask, render_template
import csv
import os
import pandas as pd

# path to book information (will change this to a database call)
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'data/cleaned_book_info.csv')

df = pd.read_csv(file_path)
titles = df['title'].tolist()
covers = df['cover'].tolist()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html",
                           zip=zip,
                           titles=titles, 
                           covers=covers)