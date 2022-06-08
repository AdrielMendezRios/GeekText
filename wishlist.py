from flask import Flask, render_template

app = Flask(__name__)

@app.route('/wishlist')

def index():
    return "<h1>Wishlist</h1>"

