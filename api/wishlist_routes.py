"""
    - Duplicate this file and rename it.
    - update blueprint name on line 24
    - on app.py: 
        - import your blueprint starting on line 8
        - register your blueprint starting on line 15
        
    - on postman or in browser: (once you've done the steps above)
        127.0.0.1:5000/route (using GET http method if your doing it through postman)
        if all went well you should see a success message.
"""
from email import message
import json
from flask import request, jsonify, Blueprint

# add your models to the models.py file then import them here
from ..models import db, Book, Author, ma, BookSchema, User
from dateutil.parser import parse
from http import HTTPStatus

# keep this if an endpoint requires caching 
from ..cache import cache

# update name-> V-----V     
api = Blueprint('wishlist_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14
@api.route("/wishlist", methods=['GET'])
@cache.cached(timeout=5) # add this decorator to cache data on GET routes (this one caches data for 5 seconds)
def routeFunction():
    return jsonify(message={"Success": f"Blueprint {api.name} configured!"})

@api.route("/wishlist", methods=['POST'])
def add_book():
    book_id = request.json['book_id']
    book = Book.query.get(book_id)

    return jsonify(book=book.as_dict()), 200

@api.route("/user", methods=['POST'])
def add_user():
    user = User(**request.json)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(msg={"Error":f"error {e}"}), 500

    return jsonify(user.as_dict()), 200

@api.route("/user/<id>", methods=['GET'])
def get_user(id):
    user = User.query.get(id)

    return jsonify(msg=user.wishlist), 200