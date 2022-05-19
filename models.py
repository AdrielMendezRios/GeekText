from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id              = db.Column(db.Integer, primary_key=True, unique=True)
    author_id       = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=True)
    price           = db.Column(db.Integer, nullable=True)
    copies_sold     = db.Column(db.Integer, nullable=True)
    date_published  = db.Column(db.Date(), nullable=True)
    genre           = db.Column(db.String(100), nullable=True)
    isbn            = db.Column(db.String(18), nullable=True, unique=True)
    description     = db.Column(db.String(250), nullable=True)
    title           = db.Column(db.String(100), nullable=True)
    publisher       = db.Column(db.String(100), nullable=True)
    
    
    # helper function to format date as iso, can be extended for further formating
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
    
    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}. Bio: {self.bio}"
    