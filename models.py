from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id              = db.Column(db.Integer, primary_key=True, unique=True)
    author_id       = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=True)
    price           = db.Column(db.Integer)
    copies_sold     = db.Column(db.Integer)
    date_published  = db.Column(db.DateTime)
    genre           = db.Column(db.String(100))
    isbn            = db.Column(db.String(100), unique=True)
    description     = db.Column(db.String(250))
    title           = db.Column(db.String(100))
    publisher       = db.Column(db.String(100))
    
    def __repr__(self) -> str:
        return f"{self.title} by {str.title(self.author.last_name)}, {str.title(self.author.first_name)} (ISBN: {self.isbn})"
    
class Author(db.Model):
    __tablename__ = 'authors'
    
    id              = db.Column(db.Integer, primary_key=True, unique=True)
    first_name      = db.Column(db.String(50), nullable=False)
    last_name       = db.Column(db.String(50), nullable=False)
    publisher       = db.Column(db.String(50), nullable=True)
    bio             = db.Column(db.String(500), nullable=True)
    books           = db.relationship('Book', backref='author')
    
    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}, \n {self.bio}"
    