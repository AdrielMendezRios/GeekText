"""
        - on postman or in browser: (once you've done the steps above)
        127.0.0.1:5000/route (using GET http method if your doing it through postman)
        if all went well you should see a success message.
"""
from email import message
import json
from flask import request, jsonify, Blueprint

from ..models import db, Book, Author, ma, BookSchema, User, Rating, Comment
from dateutil.parser import parse
from http import HTTPStatus

from ..cache import cache


api = Blueprint('rating_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14
@api.route("/route", methods=['GET'])
@cache.cached(timeout=5) # add this decorator to cache data on GET routes (this one caches data for 5 seconds)
def routeFunction():
    return jsonify(message={"Success": f"Blueprint {api.name} configured!"})