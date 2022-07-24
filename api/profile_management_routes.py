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
from flask import request, jsonify, Blueprint, make_response

# add your models to the models.py file then import them here
from ..models import db, Book, Author, ma, BookSchema, User, UserSchema
from dateutil.parser import parse
from http import HTTPStatus

from ..auth import token_required, admin_required
import jwt

# keep this if an endpoint requires caching 
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from ..cache import cache

# update name-> V-----V     
api = Blueprint('profile_management_routes', __name__)

@api.route("/user", methods=['POST'])
@token_required
def add_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    data['password'] = hashed_password
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user":user.as_dict()}), 200

@api.route("/login", methods=['POST'])
@token_required
def login():
    from ..app import app
    auth = request.authorization  
    if not auth or not auth.username or not auth.password: 
        return make_response('could not verify', 401, {'Authentication': 'login required"'})   

    user = User.query.filter_by(username=auth.username).first() 
    print(check_password_hash(user.password, auth.password)) 
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'username' : user.username, 'id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1000)}, app.config['SECRET_KEY'], "HS256")

        return jsonify({'token' : token})

    return make_response('could not verify',  401, {'Authentication': '"login required"'})  

# @api.route("/users", methods=['POST'])
# def add_user():
#     user = User (**request.json)
#     db.session.add(user)
#     db.session.commit()
#     #add if cases
#     return jsonify(msg={"in": user.as_dict()}), HTTPStatus.ACCEPTED

@api.route("/users", methods=['GET'])
@token_required
def get_user(username):
    id = request.json['id']
    user = User.query.get(id)
    print(user)
    if user is None:
        return jsonify(msg={"Error":f"User with id:{id}, does not exist."}), HTTPStatus.NOT_FOUND
    return jsonify(msg={"in": user.as_dict()}), HTTPStatus.ACCEPTED
