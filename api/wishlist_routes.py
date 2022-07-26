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
from ..models import db, Book, Author, ma, BookSchema, User, Wishlist, ShoppingCart, WishlistSchema
from dateutil.parser import parse
from http import HTTPStatus

# keep this if an endpoint requires caching 
from ..cache import cache
from ..auth import token_required, admin_required

# update name-> V-----V     
api = Blueprint('wishlist_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14

# Getting a wishlist by user_id
@api.route("/wishlist/<user_id>", methods=['GET'])
@cache.cached(timeout=5) # add this decorator to cache data on GET routes (this one caches data for 5 seconds)
@token_required
def get_wishlist(username, user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error": "No user exists"}), 404

    if user.wishlist is None:
        return jsonify({"Error": "No wishlist exists for user"})

    wishlist = Wishlist.query.get(user.wishlist.id)


    if not wishlist:
        return jsonify({"Error": "No wishlist exists"}), 404

    books = [book.as_dict() for book in wishlist.books]

    return jsonify(message={f"{user.username}'s Wishlist ": books}), 200


# Creating a wishlist for a user
@api.route("/add/wishlist", methods=['POST'])
@token_required
def add_wishlist(username):

    user = User.query.get(request.json['user_id'])
    
    if not user:
        return jsonify({"Error": "No user exists"}), 404
    
    if user.wishlist:
        return jsonify({"Error": "User already has a wishlist"})

    wishlist = Wishlist(user=user)

    try:
        db.session.add(wishlist)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(msg={"Error": f"error {e}"}), 500

    return jsonify({"user": user.as_dict(), "wishlist": wishlist.as_dict()}), 200


# Adding a book to a wishlist
@api.route("/wishlist/add", methods=['POST'])
@token_required
def add_book(username):

    user = User.query.filter_by(username=request.json['username']).first()
    
    if not user:
        return jsonify({"Error": "No user exists"}), 404
    
    if user.wishlist is None:
        return jsonify({"Error": "User does not have a wishlist"})

    wishlist = Wishlist.query.get(user.wishlist.id)
    book = Book.query.filter_by(isbn=request.json['isbn']).first()

    if not book:
        return jsonify({"Error": "No book exists"}), 404

    if not user:
        return jsonify({"Error": "No user exists"}), 404

    wishlist.books.append(book)
    db.session.commit()

    books = [book.as_dict() for book in wishlist.books]

    return jsonify({"wishlist": books}), 200


# Removing a book from a user's wishlist and adding it to the shopping cart
@api.route("/wishlist/<user_id>/remove/<isbn>", methods=['PUT'])
@token_required
def remove_book(username, user_id, isbn):

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error": "No user exists"}), 404

    if user.wishlist is None:
        return jsonify({"Error": "No wishlist exist for user"})

    wishlist = Wishlist.query.get(user.wishlist.id)
    book = Book.query.filter_by(isbn=isbn).first()

    if not wishlist:
        return jsonify({"Error": "No wishlist exists"}), 404

    if not book:
        return jsonify({"Error": "No book exists"}), 404
    elif book not in wishlist.books:
        return jsonify({"Error": "Book does not exist in wishlist"}), 404

    if user.shoppingCart is None:
        shopping_cart = ShoppingCart(user=user)
        shopping_cart.books.append(book)
        db.session.add(shopping_cart)
        db.session.commit()
    else:
        user.shoppingCart.books.append(book)

    wishlist.books.remove(book)
    db.session.commit()

    books = [book.as_dict() for book in wishlist.books]
    shopping_cart_books = [book.as_dict() for book in user.shoppingCart.books]

    return jsonify({f"{user.username}'s Wishlist": books, "Book Removed": book.as_dict(), f"{user.username}'s Shopping Cart": shopping_cart_books}), 200 