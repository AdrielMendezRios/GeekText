import json
import re
from flask import Flask, url_for, redirect, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, Book, Author
from datetime import datetime
from dateutil.parser import parse
from http import HTTPStatus

app = Flask(__name__)

isAdmin = True  # just in the mean time...

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)


@app.route("/")
def home():
    books = db.session.query(Book).all()
    authors = db.session.query(Author).all()
    return render_template("index.html", books=books, authors=authors)

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
"""
-------------------------------------------------------
                Book routes below
-------------------------------------------------------
"""
#helper function (might delete)
def isvalid_isbn(isbn: str):
    book = Book.query.filter_by(isbn=isbn).first()
    if book is not None:
        return False, {"type: ":"exists", "Error": f"Book with ISBN: {isbn} already exists"}
    
    isbn_cleaned = isbn.translate({ord("-"):None, ord(" "): None })
    if not isbn_cleaned.isalnum(): # MUST SWITCH TO .isnumeric() 
        return False, {"type: ":"format", "Error": f"Invalid ISBN: {isbn} format, must be ..."} # UPDATE
    
    return True, {}

#POST (create) book
@app.route("/books", methods=['POST'])
def add_book():
    if isAdmin:
        # check if route being called as a POST Method
        if request.method == 'POST':
            req_data = dict(request.json)
            req_data['date_published'] = parse(req_data['date_published']).date() # date to iso format
            
            # check if ID is present in body. if so, check if there exists a book with that ID already
            if 'id' in req_data:
                book = Book.query.get(req_data['id'])
                if book is not None:
                    return jsonify(msg={"Error":f"Book with ID:{req_data['id']} already exists"}), HTTPStatus.BAD_REQUEST
            
            new_book = Book(**req_data)
            isValid, msg = isvalid_isbn(req_data['isbn'])
            if not isValid:
                return jsonify(msg=msg), HTTPStatus.BAD_REQUEST
            try:
                db.session.add(new_book)
                db.session.commit()
                return jsonify(new_book.as_dict()), HTTPStatus.CREATED
            except Exception as e:
                return jsonify(msg=f"Error: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return jsonify(msg={"Error": f"HTTP code of '{request.method}' not supported by this enpoint"}), HTTPStatus.BAD_GATEWAY

# GET a book by ISBN
@app.route("/books/<isbn>", methods=['GET'])
def book_details(isbn: str):
    book = Book.query.filter_by(isbn=isbn).first()
    
    if book is None:
        return jsonify(msg={"Error": f"We dont have a book with ISBN:{isbn} in our system."}), HTTPStatus.NOT_FOUND

    if request.method == 'GET': # return existing book
        return jsonify(book.as_dict()), HTTPStatus.OK


# GET books by author  ***WIP***
@app.route("/authors/<author_id>/books", methods=['GET'])
def books_by_author(author_id):
    author = Author.query.get(author_id)
    author_books = list(author.books)
    author_name = f"{author.first_name}  {author.last_name}"
    books = [book.as_dict() for book in author_books]
    return jsonify(books_by_author={author_name:books}), HTTPStatus.ACCEPTED

# GET ALL books
@app.route("/books", methods=['GET'])
def all_books():
    books = Book.query.all() # returns list of books
    if books is None:
        return jsonify(msg={"Error:": "No books found"}), HTTPStatus.ACCEPTED
    
    books = [book.as_dict() for book in books] # convert book obj to dict and store in list of book dicts
    return jsonify(books_list=books), HTTPStatus.ACCEPTED

# PUT (update) book 
@app.route("/books", methods=['PUT'])
def update_book():
    """
        This route expects to be called with HTTP method PUT
        Header:
            content-type = application/json
        body:
        {
            "isbn": <isbn string>       <--must be included
            "key": <update value>
            ...
        }
    Returns:
        json/dict: returns a json object with updated data or error message
    """
    body = request.get_json()
    
    if 'isbn' not in body:
        return jsonify(msg={"Error" : "ISBN must be included in the body"}), HTTPStatus.BAD_REQUEST
    
    book = Book.query.filter_by(isbn=body['isbn']).first()
    if book:
        for k, v in request.json.items():
            setattr(book, k, v)
        db.session.commit()
        return jsonify(book.as_dict()), HTTPStatus.ACCEPTED
    return jsonify(msg={"Error":f"Book with ISBN: {body['isbn']} does not exist in GeekText"}), HTTPStatus.NOT_FOUND

# DELETE book
@app.route("/books", methods=['DELETE'])
def delete_book():
    book = Book.query.filter_by(isbn=request.json['isbn']).first()
    
    if book is None:
        return jsonify(msg={"Error":f"Book with ISBN {request.json['isbn']} is not in our system"}), HTTPStatus.NOT_FOUND
    
    book_data = book.as_dict()
    db.session.delete(book)
    db.session.commit()
    return jsonify(deleted_book=book_data), HTTPStatus.OK

"""
-------------------------------------------------------
                Author routes below
-------------------------------------------------------
"""
# POST (create) author
@app.route("/authors", methods=['POST'])
def add_author(fname=None, lname=None):
    if request.method == 'POST':
        new_author = Author(**request.json)
        try:
            db.session.add(new_author)
            db.session.commit()
            return jsonify(new_author.as_dict())
        except Exception as e:
            return jsonify(msg=f"Error: {e}"), 500

# GET author
@app.route("/authors/<id>", methods=['GET'])
def author_details(id):
    author = Author.query.get(id)
    
    if author is None:
        return jsonify(msg={"Error": f"Could not retreive Author with ID: {id}"}), 500
    
    if request.method == 'GET':
        return jsonify(author=author.as_dict()), 200

# GET all authors
@app.route("/authors", methods=['GET'])
def all_authors():
    authors = Author.query.all()
    authors = [author.as_dict() for author in authors]
    try:
        return jsonify(all_authors=authors)
    except Exception as e:
        return jsonify(msg=f"Error: {e}")

# PUT (update) author
@app.route("/authors", methods=['PUT'])
def update_author():
    body = request.get_json()
    author = None
    
    if 'id' not in body:
        if ('first_name' and 'last_name') not in  body:
            return jsonify(msg={"Error":f"Must provide 'id' or 'first_name' and 'last_name' attributes in request body"}), 500
        author = Author.query.filter_by(first_name=body['first_name'], last_name=body['last_name'])
    else:
        author = Author.query.get(body['id'])
    
    if author is None:
        return jsonify(msg={"Error":"Could not retrieve Author with provided data"}), 404
    
    if request.method == 'PUT':
        for k, v in request.json.items():
            setattr(author, k, v)
    db.session.commit()
    
    return jsonify(author=author.as_dict()), 200

# DELETE author
@app.route("/authors", methods=['DELETE'])
def delete_author():
    body = request.get_json()
    
    if 'id' not in body:
        if ('first_name' and 'last_name') not in  body:
            return jsonify(msg={"Error":f"Must provide 'id' or 'first_name' and 'last_name' attributes in request body"}), 500
        author = Author.query.filter_by(first_name=body['first_name'], last_name=body['last_name'])
    else:
        author = Author.query.get(body['id'])
    
    if author is None:
        return jsonify(msg={"Error":"Could not retrieve Author with provided data"}), 404
    
    author_data = author.as_dict()
    db.session.delete(author)
    db.session.commit()
    return jsonify(deleted_author=author_data), 200

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run()