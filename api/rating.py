"""
        - on postman or in browser: (once you've done the steps above)
        127.0.0.1:5000/route (using GET http method if your doing it through postman)
        if all went well you should see a success message.
"""
from email import message
import json
from flask import request, jsonify, Blueprint
from flask import Flask, url_for, render_template

from ..models import db, Book, Author, ma, BookSchema, User, Rating, Comment
from dateutil.parser import parse
from http import HTTPStatus

from ..cache import cache


api = Blueprint('rating_routes', __name__)

@api.route('/rating',methods=['GET','POST'])
def home():
        #return jsonify(message={"Success": f"Blueprint {api.name} configured!"})
 return render_template ('starRating.html')