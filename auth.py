from functools import wraps
from flask import request, jsonify
import jwt
from http import HTTPStatus
# from models import User

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            from .app import app
            from .models import User
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            
        if not token:
            return jsonify({'msg':'a valid token is missing'})
        try:
            from .app import app
            from .models import User
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user.isAdmin:
                return jsonify({'message': 'user is not an Admin'}), HTTPStatus.UNAUTHORIZED
        except Exception as e:
            print("exception: ",e)
            return jsonify({'message':'token provided is invalid'}), HTTPStatus.UNAUTHORIZED
        
        

        return f(current_user, *args, **kwargs)
    return decorator