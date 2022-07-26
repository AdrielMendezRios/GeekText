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
from ..models import db, Book, Author, ma, BookSchema, User, UserSchema, CreditCard, CreditCardSchema
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

@api.route("/create-user", methods=['POST'])
def add_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    data['password'] = hashed_password
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user":user.as_dict()}), 200

@api.route("/get-token", methods=['POST'])
def login():
    from ..app import app
    auth = request.authorization  
    if not auth or not auth.username or not auth.password: 
        return make_response('could not verify', 401, {'Authentication': 'login required"'})   

    user = User.query.filter_by(username=auth.username).first() 
    if not user:
        return jsonify({"message":"user not found"}), 404
    print(check_password_hash(user.password, auth.password)) 
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'username' : user.username, 'id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1000)}, app.config['SECRET_KEY'], "HS256")

        return jsonify({'token' : token})

    return make_response('could not verify',  401, {'Authentication': '"login required"'})  

@api.route("/user", methods=['GET'])
def get_user():
    id = request.json['id']
    user = User.query.get(id)
    if user is None:
        return jsonify(msg={"Error":f"User with id:{id}, does not exist."}), HTTPStatus.NOT_FOUND
    return jsonify(msg={"in": user.as_dict()}), HTTPStatus.ACCEPTED

# route that returns all credit cards for a user given the users username
@api.route("/credit-cards", methods=['GET'])
@token_required
def get_credit_cards(username):
    user_name = request.json['username']
    user = User.query.filter_by(username=user_name).first()
    if username != user_name:
        return jsonify({"Error": "you are not authorized to view this data"}), HTTPStatus.UNAUTHORIZED
    if user is None:
        return jsonify(msg={"Error":f"User with username:{username}, does not exist."}), HTTPStatus.NOT_FOUND
    credit_cards = CreditCard.query.filter_by(user_id=user.id).all()
    credit_cards_schema = CreditCardSchema(many=True)
    return jsonify(credit_cards_schema.dump(credit_cards)), HTTPStatus.ACCEPTED

# create endpoint that adds a new credit card to the users creditCard column
@api.route("/add-cc", methods=['POST'])
@token_required
def add_cc(username):
    user = User.query.filter_by(username=request.json['username']).first()
    if username != user.username:
        return jsonify({"Error": "You are not authorized to add a credit card to this user."}), HTTPStatus.UNAUTHORIZED
    if user is None:
        return jsonify({"Error":"User does not exist."}), HTTPStatus.NOT_FOUND
    cc = request.json['credit_card']
    creditCard = CreditCard(user=user, credit_card=cc)
    
    try:
        db.session.add(creditCard)
        db.session.commit()
    except Exception as e:
        print("Error: ", e)
        return jsonify({"Error":f"Error adding credit card to user:{user.username}"}), HTTPStatus.NOT_FOUND
    schema = CreditCardSchema()
    credit_cards_schema = CreditCardSchema()
    return jsonify(credit_cards_schema.dump(creditCard)), HTTPStatus.ACCEPTED

# define endpoint that retrieves the first credit card for a user
@api.route("/get-cc", methods=['GET'])
@token_required
def get_cc(username):
    user_name = request.json['username']
    user = User.query.filter_by(username=user_name).first()
    if username != user_name:
        return jsonify({"Error": f"You do not have access to this information"}), HTTPStatus.UNAUTHORIZED
    if user is None:
        return jsonify({"Error":f"User with username:{username}, does not exist."}), HTTPStatus.NOT_FOUND
    credit_card = CreditCard.query.filter_by(user_id=user.id).first()
    credit_cards_schema = CreditCardSchema()
    return jsonify(credit_cards_schema.dump(credit_card)), HTTPStatus.ACCEPTED

# {f"New Credit Card added": creditCard.credit_card, "user":user.username}