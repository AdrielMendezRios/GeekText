from sqlalchemy.exc import IntegrityError
from flask import request, jsonify, Blueprint
from ..models import db, Book, Author, ma, BookSchema, AuthorSchema
from dateutil.parser import parse
from http import HTTPStatus
from ..cache import cache
from ..auth import token_required, admin_required


# import datetime
# from werkzeug.security import generate_password_hash,check_password_hash
# import jwt

api = Blueprint('author_routes', __name__)

isAdmin = True

# POST (create) author
@api.route("/authors", methods=['POST'])
@admin_required
def add_author(username):
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
        if e.__class__ is IntegrityError:
            db.session.rollback()
            return jsonify(message={"Error":"fatal error. Rolling back db session."})
        return jsonify({"message": {e}}), HTTPStatus.INTERNAL_SERVER_ERROR
    

# GET author
@api.route("/authors/<id>", methods=['GET'])
@cache.cached(timeout=5)
@token_required
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
@api.route("/authors", methods=['GET'])
@cache.cached(timeout=5)
@token_required
def all_authors(username):
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
@api.route("/authors/<author_id>/books", methods=['GET'])
@cache.cached(timeout=5)
@token_required
def books_by_author(username, author_id):
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
@api.route("/authors", methods=['PUT'])
@admin_required
def update_author(username):
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
@api.route("/authors", methods=['DELETE'])
@admin_required
def delete_author(username):
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










































