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
from ..models import db, Book, Author, ma, BookSchema, User, ShoppingCart
from dateutil.parser import parse
from http import HTTPStatus

# keep this if an endpoint requires caching 
from ..cache import cache

# update name-> V-----V     
api = Blueprint('shopping_cart_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14
@api.route("/route", methods=['GET'])
@cache.cached(timeout=5) # add this decorator to cache data on GET routes (this one caches data for 5 seconds)
def routeFunction():
    return jsonify(message={"Success": f"Blueprint {api.name} configured!"})


@api.route("/shopping_cart", methods=['POST'])  
def add_shopping_cart():
    username = request.json['username']
    user = User.query.filter_by(username=username).first()
    shopping_cart = ShoppingCart(user=user)

    try:
        db.session.add(shopping_cart)
        db.session.commit()
    except Exception as e:
        return jsonify({"Error": "something went wrong"}), 500

    return jsonify({"user": user.as_dict(), "shopping cart": shopping_cart.as_dict()}), 200

@api.route("/adduser", methods=['POST'])
def adduser():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.as_dict()}), 200    

@api.route("/shopping_cart", methods=['PUT'])
def update_shopping_cart():
    if not 'username' in request.json:
        return jsonify({"Error": "Did not provide username in request body"}), 500
    if not 'isbn' in request.json:
        return jsonify({"Error": "Did not provide isbn in request body"}), 500   
    username=request.json['username']
    isbn=request.json['isbn']


    user = User.query.filter_by(username=username).first()
    book = Book.query.filter_by(isbn=isbn).first()

    if user.shoppingCart is None:
        shopping_cart = ShoppingCart(user=user,book=book)
        try:
            db.session.add(shopping_cart)
            db.session.commit()
        except Exception as e:
            return jsonify({"Error": "something went wrong"}), 500

    else: 
        try:
            shopping_cart=ShoppingCart.query.get(user.shoppingCart.id)
            shopping_cart.books.append(book)
            db.session.add(shopping_cart)
            db.session.commit()

        except Exception as e:
            print (e.text)
            return jsonify({"Error": "something went wrong"}), 500            

    books = user.shoppingCart.books 
    print("\n\n\n", dir(books), "\n\n\n")
    books = [book.as_dict() for book in books]

    return jsonify({"shopping_cart":books}), 200      

@api.route("/deletebook", methods=['PUT'])
def delete_book():
    user = request.json['username']
    book = request.json['isbn']

    user = User.query.filter_by(username=username).first()
    books = User.shoppingCart.books

    if book.isbn == request.json['isbn']:
        books.remove(book)
    db.session.commit()    

@api.route("/retrieve_shopping_cart", methods = ['GET'])   
def retrieve_shopping_cart():
    username=request.json['username']

    user = User.query.filter_by(username=username).first()

    books = user.shoppingCart.books
    books = [book.as_dict() for book in books]

    return jsonify({"shopping_cart":books}), 200      




#new delete book route
    #user = User.query.filter_by(username=username)
    #books = user.shoppingCart.books
#for book in books:
    #if book.isbn == request.json['isbn']:
        #books.remove(book)
#db.session.commit()    
    
#new retrieve shopping cart route
    #use lines 88,90, 92

