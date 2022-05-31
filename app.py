from flask import Flask, url_for, redirect, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, Book, Author, ma, BookSchema, AuthorSchema
from dateutil.parser import parse
from http import HTTPStatus
from flask_caching import Cache
# from marshmallow import ValidationError, pprint
# from datetime import date


# create flask app 
app = Flask(__name__)

# create cache obj
cache = Cache() 

# config cache
app.config['CACHE_TYPE'] = 'simple'

# database configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# migrate config
migrate = Migrate(app, db, render_as_batch=True)

# init database, Marshmallow & cache
db.init_app(app)
ma.init_app(app)
cache.init_app(app)

# place holder for eventual user auth
isAdmin = True  # just in the mean time...

@app.route("/")
def home():
    db.session.rollback()
    books = db.session.query(Book).all()
    authors = db.session.query(Author).all()
    return render_template("index.html", books=books, authors=authors)

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                Book routes below
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""


# POST (create) book
@app.route("/books", methods=['POST'])
def add_book():
    """ This endpoint creates a new book with given request body
        HTTP Method: POST
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |      id           |   Integer |      No       | auto generated. don't         |
        |                   |           |               | include                       |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      isbn         |   string  |      Yes      |       Primary Key             |
        |                   |           |               |  string must ONLY include     |
        |                   |           |               |  numbers, '-' or spaces       |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |  date_publsihed   |   date    |      yes      | should be in format:          |
        |                   |  string   |               | "YYYY-MM-DD"                  |
        |                   |           |               | i.e "2022-05-25"              |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      Title        |   string  |      Yes      |   Name of the book            |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |      price        |   Integer |      Yes      |   Defaults to 25, if not      |
        |                   |           |               |   include                     |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      genre        |   string  |      Yes      |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |   copies_sold     |   Integer |      no       |   Defaults to 0, if not       |
        |                   |           |               |   included                    |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   description     |   string  |      Yes      |  up to 500 chars              |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |   author_id       |   Integer |     Yes       |   Foreign Key                 |
        |                   |           |               |   author_id must exist in     |
        |                   |           |               |   server                      |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   publisher       |   string  |      Yes      |   name of the publisher       |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
    Example body:
        {
                "author_id": 5,
                "date_published": "2022-05-22",
                "description": "a book about things",
                "genre": "horror",
                "isbn": "1-87-876587-9879",
                "price": 25,
                "publisher": "penguin",
                "title": "cien años de soledad"
        }
    Returns:
        successful:
            json response: returns the body you provided
        unsuccessful:
            json response: returns a json error message
        
    """
    if isAdmin:
        # copy json into req_data
        body = dict(request.json)
        
        #validate request body data
        schema = BookSchema()
        invalid_msg = schema.validate(body)
        if invalid_msg:
            return jsonify(invalid_msg), HTTPStatus.BAD_REQUEST
        
        # convert date_published string to python date obj
        body['date_published'] = parse(body['date_published']).date()
            
        # check if ID is present in body. if so, check if there exists a book with that ID already
        if 'id' in body:
            book = Book.query.get(body['id'])
            if book is not None:
                return jsonify(message={"Error":f"Book with ID:{body['id']} already exists"}), HTTPStatus.BAD_REQUEST

        # create book obj
        new_book = Book(**body)
        
        # add to authors books list
        if 'author_id' in body:
            author = Author.query.get(body['author_id'])
            new_book.author = author
        
        try:
            db.session.add(new_book)
            db.session.commit()
            return jsonify(new_book.as_dict()), HTTPStatus.CREATED # 201
        except Exception as e:
            return jsonify(message={"Error": e}), HTTPStatus.INTERNAL_SERVER_ERROR

# GET a book by ISBN
@app.route("/books/<isbn>", methods=['GET'])
@cache.cached(timeout=5)
def book_details(isbn: str):
    """ This endpoint returns the book for a given ISBN
        HTTP Method: GET
        Headers:
            content-type = application/json
        authentication: user (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      isbn         |   string  |      Yes      |       Primary Key             |
        |                   |           |               |  string must ONLY include     |
        |                   |           |               |  numbers, '-' or spaces       |
        |___________________|___________|_______________|_______________________________|
        Body Example:
            {
                "isbn": "1-87-876587-9879"
            }
        Returns:
            successful:
                json response: returns the book with the ISBN provided
            unsuccessful:
                json response: returns a json error message
        
    """
    book = Book.query.filter_by(isbn=isbn).first()
    
    if book is None:
        return jsonify(message={"Error": f"We dont have a book with ISBN:{isbn} in our system."}), HTTPStatus.NOT_FOUND

    return jsonify(book.as_dict()), HTTPStatus.OK

# GET ALL books
@app.route("/books", methods=['GET'])
@cache.cached(timeout=5)
def all_books():
    """ This endpoint returns all books in server
        HTTP Method: GET
        Headers:
            content-type = application/json
        authentication: user (TODO)
        available parameters: None needed
        Returns:
            successful:
                json response: returns a list of all books in server
            unsuccessful:
                json response: returns a json error message
    """
    books = Book.query.all() # returns list of books
    
    if books is None:
        return jsonify(message={"Error:": "No books found"}), HTTPStatus.NOT_FOUND
    
    # convert book obj to dict and store in list of book dicts
    books = [book.as_dict() for book in books] 
    return jsonify(books_list=books), HTTPStatus.OK

# PUT (update) book 
@app.route("/books", methods=['PUT'])
def update_book():
    """ This endpoint updates a book with ISBN provided
        HTTP Method: PUT
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      isbn         |   string  |      Yes      |  needed to find book          |
        |                   |           |               |  cannot be changed            |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |  date_publsihed   |   date    |      no       | should be in format:          |
        |                   |  string   |               | "YYYY-MM-DD"                  |
        |                   |           |               | i.e "2022-05-25"              |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      Title        |   string  |      no       |   updated book name           |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |      price        |   Integer |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      genre        |   string  |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |   copies_sold     |   Integer |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   description     |   string  |      no       |  upto 500 chars               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |   author_id       |   Integer |     no        |   Foreign Key                 |
        |                   |           |               |   author_id must exist        |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   publisher       |   string  |     no        |   name of the publisher       |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
    Example:
        {
            "description": "a book about things UPDATED",
            "genre": "horror UPDATE",
            "isbn": "1-87-876587-9879",
            "price": 25,
        }
    Returns:
        successful:
            json response: returns the updated book
        unsuccessful:
            json response: returns a json error message
        
    """
    body = request.get_json()
    
    # validate data
    schema = BookSchema()
    invalid_msg = schema.validate(request.json, session=db.session)
    if invalid_msg:
        return jsonify(invalid_msg), HTTPStatus.BAD_REQUEST
    
    if 'isbn' not in body:
        return jsonify(message={"Error" : "ISBN must be included in the body"}), HTTPStatus.BAD_REQUEST
    
    book = Book.query.filter_by(isbn=body['isbn']).first()
    
    if book is None:
        return jsonify(message={"Error":f"Retrieving book with ISBN: {body['isbn']}"}), HTTPStatus.NOT_FOUND
    
    # update book info, should rewrite to include try/except block.
    if book:
        for k, v in request.json.items():
            # 'author' is an ORM token now, which raises an AttributeException error. 
            # so if a key called 'author' is passed it should be ignored
            if k != "author": 
                setattr(book, k, v)
        db.session.commit()
        return jsonify(book.as_dict()), HTTPStatus.ACCEPTED
    return jsonify(message={"Error":f"Book with ISBN: {body['isbn']} does not exist in GeekText"}), HTTPStatus.NOT_FOUND

# DELETE book
@app.route("/books", methods=['DELETE'])
def delete_book():
    """ This endpoint deletes book with given ISBN
        HTTP Method: DELETE
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |                   |           |               |       Primary Key             |
        |      isbn         |  string   |       Yes     |  string must ONLY include     |
        |                   |           |               |  numbers, '-' or spaces       |
        |___________________|___________|_______________|_______________________________|
        Body Example:
            {
                "isbn": "1-87-876587-9879"
            }
        Returns:
            successful:
                json response: returns the book with the ISBN provided
            unsuccessful:
                json response: returns a json error message
        
    """
    book = Book.query.filter_by(isbn=request.json['isbn']).first()
    
    if book is None:
        return jsonify(message={"Error":f"Book with ISBN {request.json['isbn']} is not in our system"}), HTTPStatus.NOT_FOUND
    
    book_data = book.as_dict()
    db.session.delete(book)
    db.session.commit()
    return jsonify(deleted_book=book_data), HTTPStatus.OK
"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                Book routes above
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                Author routes below
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""
# POST (create) author
@app.route("/authors", methods=['POST'])
def add_author(fname=None, lname=None):
    """ This endpoint creates a new Author
        HTTP Method: POST
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |                   |           |               |     Primary key               |
        |      id           |   Integer |      No       |   auto generated. don't       |
        |                   |           |               |   include                     |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   first_name      |   string  |      Yes      |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   last_name       |   string  |      Yes      |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   publisher       |   string  |      Yes      |   name of the publisher       |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        Example:
            {
                "first_name" : "Gabriel",
                "last_name"  : "Garcia Marquez",
                "publisher"  : "Penguin"
            }
        Returns:
            successful:
                json response: returns created author in json format
            unsuccessful:
                json response: returns a json error message
    """
    schema = AuthorSchema()
    invalid_msg = schema.validate(request.json)
    if invalid_msg:
        return jsonify(invalid_msg), HTTPStatus.BAD_REQUEST
    
    new_author = Author(**request.json)
    
    if new_author is None:
        return jsonify({"message":"Could not create author with provided data", "request body": request.json}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # prob can remove the try block
    try:
        db.session.add(new_author)
        db.session.commit()
        return jsonify(new_author.as_dict()), HTTPStatus.CREATED
    except Exception as e:
        return jsonify({"message": {e}}), HTTPStatus.INTERNAL_SERVER_ERROR

# GET author
@app.route("/authors/<id>", methods=['GET'])
@cache.cached(timeout=5)
def author_details(id):
    """ This endpoint returns an author
        HTTP Method: GET
        Headers:
            content-type = application/json
        authentication: user (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      id           |  Integer  |      Yes      |       Primary Key             |
        |___________________|___________|_______________|_______________________________|
        Body Example:
            {
                "id": 1
            }
        Returns:
            successful:
                json response: returns the author with given id
            unsuccessful:
                json response: returns a json error message
        
    """
    author = Author.query.get(id)
    
    if author is None:
        return jsonify(msg={"message": f"Could not retreive Author with ID: {id}"}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return jsonify(author=author.as_dict()), HTTPStatus.OK

# GET all authors
@app.route("/authors", methods=['GET'])
@cache.cached(timeout=5)
def all_authors():
    """ This endpoint returns all authors in server
        HTTP Method: GET
        Headers:
            content-type = application/json
        authentication: user (TODO)
        available parameters: None
        Returns:
            successful:
                json response: returns a list of all authors in server
            unsuccessful:
                json response: returns a json error message
    """
    authors = Author.query.all()

    if authors == {}:
        return jsonify(msg={"message":"No authors found"}), HTTPStatus.NOT_FOUND
    
    # create a list of authors converted as dicts
    authors = [author.as_dict() for author in authors]
    
    return jsonify(all_authors=authors), HTTPStatus.OK


# GET books by author
@app.route("/authors/<author_id>/books", methods=['GET'])
@cache.cached(timeout=5)
def books_by_author(author_id):
    """ This endpoint returns an author
        HTTP Method: GET
        Headers:
            content-type = application/json
        authentication: user (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      id           |  Integer  |      Yes      |       Primary Key             |
        |___________________|___________|_______________|_______________________________|
        Body Example:
            {
                "id": 1
            }
        Returns:
            successful:
                json response: returns a list of book for the given author id
            unsuccessful:
                json response: returns a json error message
    """
    author = Author.query.get(author_id)
    
    if author is None:
        return jsonify({"message": f"No author with ID: {author_id} in our system"}), HTTPStatus.NOT_FOUND
    
    author_books = list(author.books)
    author_name = f"{author.first_name} {author.last_name}"
    
    # creates a list of books converted as dicts
    books = [book.as_dict() for book in author_books]
    return jsonify(books_by_author={"total":len(books), author_name:books}), HTTPStatus.OK


# PUT (update) author
@app.route("/authors", methods=['PUT'])
def update_author():
    """ This endpoint updates author with provided id
        HTTP Method: PUT
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |
        |                   |           |               |                               |
        |      id           |   Integer |      Yes      |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   first_name      |   string  |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   last_name       |   string  |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |   publisher       |   string  |      no       |                               |
        |                   |           |               |                               |
        |___________________|___________|_______________|_______________________________|
    Example:
        {
            "first_name" : "Gabriel",
            "last_name"  : "Garcia Marquez",
            "publisher"  : "Penguin"
        }
    Returns:
        successful:
            json response: returns created author in json format
        unsuccessful:
            json response: returns a json error message
    """
    body = request.get_json()
    author = None
    
    schema = AuthorSchema()
    invalid_msg = schema.validate(body)
    if invalid_msg:
        return jsonify(invalid_msg), HTTPStatus.BAD_REQUEST
    
    if body == {}:
        return jsonify({"message":"No content provided"}), HTTPStatus.NO_CONTENT
    
    if 'id' not in body:
        if ('first_name' and 'last_name') not in  body:
            return jsonify(msg={"Error":f"Must provide 'id' or 'first_name' and 'last_name' attributes in request body"}), HTTPStatus.BAD_REQUEST
        author = Author.query.filter_by(first_name=body['first_name'], last_name=body['last_name'])
    else:
        author = Author.query.get(body['id'])
    
    if author is None:
        return jsonify(msg={"Error":"Could not retrieve Author with provided data"}), HTTPStatus.NOT_FOUND
    
    for k, v in request.json.items():
        setattr(author, k, v)
    db.session.commit()
    
    return jsonify(author=author.as_dict()), HTTPStatus.OK

# DELETE author (should prob never be used unless you're testing)
@app.route("/authors", methods=['DELETE'])
def delete_author():
    """ This endpoint deletes Author with given ID
        HTTP Method: DELETE
        Headers:
            content-type = application/json
        authentication: Admin (TODO)
        available parameters:
        |      Name         |   Type    |   Required    |           Comments            |            
        |___________________|___________|_______________|_______________________________|
        |                   |           |               |                               |           
        |      id           |   Integer |      Yes      |                               |
        |___________________|___________|_______________|_______________________________|
        Body Example:
            {
                "id": 3
            }
        Returns:
            successful:
                json response: returns the author with the id provided
            unsuccessful:
                json response: returns a json error message
        
    """
    body = request.get_json()
    
    if 'id' not in body:
        if ('first_name' and 'last_name') not in  body:
            return jsonify(msg={"Error":f"Must provide 'id' or 'first_name' and 'last_name' attributes in request body"}), HTTPStatus.BAD_REQUEST
        author = Author.query.filter_by(first_name=body['first_name'], last_name=body['last_name'])
    else:
        author = Author.query.get(body['id'])
    
    if author is None:
        return jsonify(msg={"Error":"Could not retrieve Author with provided data"}), HTTPStatus.NOT_FOUND
    
    author_data = author.as_dict()
    db.session.delete(author)
    db.session.commit()
    return jsonify(deleted_author=author_data), HTTPStatus.OK

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                Author routes above
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

# something went really bad
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify(error_msg={"code":error.code, "description": error.description}), HTTPStatus.INTERNAL_SERVER_ERROR

# for undefined endpoints
@app.errorhandler(404)
def not_found_error(error):
    return jsonify(error_msg={"code":error.code, "description": error.description}), HTTPStatus.NOT_FOUND


# @app.route("books/bulk_update", methods=['PUT'])
# def bulk_update(key: str, value):
#     books = db.session.query(Book).all()
#     for book in books:
#         setattr(book, key, value)
#         db.session.commit()
#     books = [book.as_dict() for book in books]
#     return jsonify(books), 200
        
if __name__ == "__main__":
    app.run()