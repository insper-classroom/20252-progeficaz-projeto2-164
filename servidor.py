from flask import Flask, render_template_string, request, redirect
from views import *
from utils import *

app = Flask(__name__)
app.static_folder = 'static'

if __name__ == "__main__":
    app.run(debug=True)
