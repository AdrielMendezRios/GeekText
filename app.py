import json
import re
from flask import Flask, url_for, redirect, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, Book, Author
from datetime import datetime
from dateutil.parser import parse

app = Flask(__name__)

isAdmin = True  # just in the mean time...

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

@app.route("/")
def home():
    books = db.session.query(Book).all()
    return render_template("index.html", books=books)


"""
    Adriels' TODOs:
    Book Details 
    [~] An administrator must be able to create a book with the book ISBN, book
        name, book description, price, author, genre, publisher, year published and
        copies sold.
    [~] Must be able retrieve a book's detail
    [~] An administrator must be able to create an author with first name, 
        last name, biography and publisher
    [~] Must be able to retrieve a list of books associate with an author
"""
# made it its own route for now 
@app.route("/add_book", methods=['POST'])
def add_book():
    if isAdmin:
        # check if route being called as a POST Method
        if request.method == 'POST':
            req_data = dict(request.json)
            req_data['date_published'] = parse(req_data['date_published']).date()
            new_book = Book(**req_data)
            try:
                db.session.add(new_book)
                db.session.commit()
                return jsonify(new_book.as_dict()), 202
            except Exception as e:
                return jsonify(msg=f"Error: {e}"), 400
        else:
            return jsonify(msg={"Error": f"HTTP code of '{request.method}' not supported by this enpoint"})

# GET book, PUT (update) book, DELETE book
@app.route("/book/<id>", methods=['GET', 'PUT', 'DELETE'])
def book_details(id):
    book = Book.query.get(id)
    
    if book is None:
        return jsonify(msg={"Error": f"Could not retreive author with ID:{id} or does not exists"}), 500
    
    if request.method == 'GET': # return existing book
        return jsonify(book.as_dict())
    elif request.method == 'PUT': # update existing book 
        for k, v in request.json.items():
            setattr(book, k, v)
        db.session.commit()
        return jsonify(book.as_dict())
    elif request.method == 'DELETE': # Delete book from db
        book_data = book.as_dict()
        db.session.delete(book)
        db.session.commit()
        return jsonify(delete_book=book_data)
        
@app.route("/all_books")
def all_books():
    books = Book.query.all() # returns list of books
    if books is not None:
        books = [book.as_dict() for book in books] # convert book obj to dict and store in list
        return jsonify(books_list=books), 202
    elif books is None:
        return jsonify(msg={"Error:": "No books found"})
    else:
        pass

@app.route("/add_author", methods=['POST'])
def add_author(fname=None, lname=None):
    if request.method == 'POST':
        new_author = Author(**request.json)
        try:
            db.session.add(new_author)
            db.session.commit()
            return jsonify(new_author.as_dict())
        except Exception as e:
            return jsonify(msg=f"Error: {e}"), 500

# GET author, PUT (update) author, DELETE author
@app.route("/author/<id>", methods=['GET', 'PUT', 'DELETE'])
def author_details(id):
    author = Author.query.get(id)
    
    if author is None:
        return jsonify(msg={"Error": f"Could not retreive Author with ID: {id}"}), 500
    
    if request.method == 'GET':
        return jsonify(author=author.as_dict()), 200
    elif request.method == 'PUT':
        for k, v in request.json.items():
            setattr(author, k, v)
        db.session.commit()
        return jsonify(author=author.as_dict()), 200
    elif request.method == 'DELETE':
        author_data = author.as_dict()
        db.session.delete(author)
        db.session.commit()
        return jsonify(deleted_author=author_data), 200

        
        
@app.route("/all_authors")
def all_authors():
    authors = Author.query.all()
    authors = [author.as_dict() for author in authors]
    try:
        return jsonify(all_authors=authors)
    except Exception as e:
        return jsonify(msg=f"Error: {e}")

@app.route("/author/<author_id>/books", methods=['GET'])
def books_by_author(author_id):
    author = Author.query.get(author_id)
    author_books = list(author.books)
    author_name = f"{author.first_name}  {author.last_name}"
    books = [book.as_dict() for book in author_books]
    return jsonify(books_by_author={author_name:books})

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run()