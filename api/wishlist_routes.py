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
from ..models import db, Book, Author, ma, BookSchema, User, Wishlist, ShoppingCart
from dateutil.parser import parse
from http import HTTPStatus

# keep this if an endpoint requires caching 
from ..cache import cache

# update name-> V-----V     
api = Blueprint('wishlist_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14


@api.route("/wishlist/<id>", methods=['GET'])
@cache.cached(timeout=5) # add this decorator to cache data on GET routes (this one caches data for 5 seconds)
def routeFunction(id):

    wishlist = Wishlist.query.get(id)

    return jsonify(message={"Wishlist ":wishlist.as_dict()})


# Creating a user and their wishlist
@api.route("/user", methods=['POST'])
def add_user():
    user = User(**request.json)

    wishlist = Wishlist(user=user)
    shopping_cart = ShoppingCart(user=user)

    try:
        db.session.add(user)
        db.session.add(wishlist)
        db.session.add(shopping_cart)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(msg={"Error":f"error {e}"}), 500

    return jsonify({"user":user.as_dict(), "wishlist":wishlist.as_dict()}), 200


# Getting a user's wishlist by its id
@api.route("/user/<id>", methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    # wishlist = Wishlist.query.filter_by(wishlist_id=user.wishlist_id)

    return jsonify({"user":user.as_dict(), "wishlist":user.wishlist.as_dict()}), 200