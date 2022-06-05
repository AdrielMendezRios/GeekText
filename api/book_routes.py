from sqlalchemy.exc import IntegrityError
from flask import request, jsonify, Blueprint
from ..models import db, Book, Author, ma, BookSchema
from dateutil.parser import parse
from http import HTTPStatus
from ..cache import cache

api = Blueprint('book_routes', __name__)

isAdmin = True

# POST (create) book
@api.route("/books", methods=['POST'])
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
        |   author_id       |   Integer |      Yes      |   Foreign Key                 |
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
        
        # check if isbn already exist
        if 'isbn' in body:
            book = Book.query.filter_by(isbn=body['isbn']).first()
            if book is not None:
                return jsonify(
                    message={"Error":f"Book with ISBN:{body['isbn']} already exists."}), HTTPStatus.FORBIDDEN
        
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
            if e.__class__ is IntegrityError:
                db.session.rollback()
                return jsonify(message={"Error":"fatal error. Rolling back db session."})
            return jsonify(message={"Error": e}), HTTPStatus.INTERNAL_SERVER_ERROR

# GET a book by ISBN
@api.route("/books/<isbn>", methods=['GET'])
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
@api.route("/books", methods=['GET'])
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
@api.route("/books", methods=['PUT'])
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
@api.route("/books", methods=['DELETE'])
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


