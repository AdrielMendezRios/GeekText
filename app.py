from flask import Flask, url_for, redirect, render_template, request, jsonify
from flask_migrate import Migrate
from .models import db, Book, Author, ma, BookSchema, AuthorSchema
from dateutil.parser import parse
from http import HTTPStatus
from .cache import cache

# import blueprint api routes below
# from .api.blueprintTemplate import api as whateverIcalledItHere
from .api.book_routes import api as book_routes
from .api.author_routes import api as author_routes
from .api.wishlist_routes import api as wishlist_routes
from .api.shopping_cart import api as shopping_cart_routes


# create flask app 
app = Flask(__name__)


# Register route blueprints below
# app.register_blueprint(whateverIcalledItHere)
app.register_blueprint(book_routes)
app.register_blueprint(author_routes)
app.register_blueprint(wishlist_routes)
app.register_blueprint(shopping_cart_routes)

# config cache
app.config['CACHE_TYPE'] = 'simple'

# database configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# migrate config
migrate = Migrate(app, db, render_as_batch=True)

# init database, Marshmallow & cache
db.init_app(app)
ma.init_app(app)
cache.init_app(app)

# place holder for eventual user auth
isAdmin = True  # just in the mean time...

@app.route("/")
def home():
    db.session.rollback()
    books = db.session.query(Book).all()
    authors = db.session.query(Author).all()
    return render_template("index.html", books=books, authors=authors)

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

# something went really bad
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify(error_msg={"code":error.code, "description": error.description}), HTTPStatus.INTERNAL_SERVER_ERROR

# for undefined endpoints
@app.errorhandler(404)
def not_found_error(error):
    return jsonify(error_msg={"code":error.code, "description": error.description}), HTTPStatus.NOT_FOUND

if __name__ == "__main__":
    app.run()