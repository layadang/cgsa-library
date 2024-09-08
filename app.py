# terminal run $ flask --app app --debug run
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    var = "Daniel"
    return render_template("index.html", name=var)