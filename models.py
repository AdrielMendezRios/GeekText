from dataclasses import fields
from flask_sqlalchemy import SQLAlchemy
from datetime import  date
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, validates, RAISE, fields, pprint

db = SQLAlchemy()
ma = Marshmallow()


class Book(db.Model):
    __tablename__ = 'books'
    
    id              = db.Column(db.Integer,     primary_key=True, unique=True)
    author_id       = db.Column(db.Integer,     db.ForeignKey('authors.id'), nullable=True)
    price           = db.Column(db.Integer,     default=25)
    copies_sold     = db.Column(db.Integer,     default=0)
    date_published  = db.Column(db.Date(),      nullable=True)
    genre           = db.Column(db.String(100), nullable=True)
    isbn            = db.Column(db.String(18),  unique=True)
    description     = db.Column(db.String(250), nullable=True)
    title           = db.Column(db.String(100), nullable=True)
    publisher       = db.Column(db.String(100), nullable=True)
    
    
    # helper function to format date for as_dict function
    def set_value(self, name):
        val = getattr(self, name)
        if type(val) is date:
            return val.isoformat()
        return val

    def as_dict(self):
        return {c.name: self.set_value(c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"{self.title} by {str.title(self.author.last_name)}, {str.title(self.author.first_name)} (ISBN: {self.isbn})"
    
class Author(db.Model):
    __tablename__ = 'authors'
    
    id              = db.Column(db.Integer, primary_key=True, unique=True)
    first_name      = db.Column(db.String(50), nullable=True)
    last_name       = db.Column(db.String(50), nullable=True)
    publisher       = db.Column(db.String(50), nullable=True)
    bio             = db.Column(db.String(500), nullable=True)
    books           = db.relationship('Book', backref='author')
    

    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"{self.first_name} {self.last_name}. Bio: {self.bio}"

"""
    the class below are Marshmallow schema classes for the sqlalchemy classes above.
    i use them for validation but can also be used for (de)serializing the ORM objects
"""

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_relationships = True
        include_fk = True
        dateformat = '%Y-%m-%d'
        unknown = RAISE
    
    @validates('isbn')
    def validate_isbn(self, val):
        isbn_cleaned = val.translate({ord("-"):None, ord(" "): None }) # remove "-" and spaces from isbn string
        if not isbn_cleaned.isnumeric():
            raise ValidationError(f"Invalid ISBN: {val}. must be a string containing ONLY numbers, '-' or a spaces ")

class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        include_relationships = True
        include_fk = True

    books = fields.Nested(BookSchema, many=True)

