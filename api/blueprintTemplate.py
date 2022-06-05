"""
    Duplicate this file and rename it.
    on app.py: 
        import your blueprint starting on line 8
        register your blueprint starting on line 15
"""
from flask import request, jsonify, Blueprint

# add your models to the models.py file then import them here
from ..models import db, Book, Author, ma, BookSchema
from dateutil.parser import parse
from http import HTTPStatus

# keep this if an endpoint requires cahcing 
from ..cache import cache

# update!       V-------------V     
api = Blueprint('<name>_routes', __name__)

# example route definition
# the decorator below starts with `@api` because that what the blueprint was name on line 14
@api.route("/route/<param>")
@cache.cached(timeout=5) # add this decorator to cache data (this one caches data for 5 seconds)
def routeFunction(param):
    pass