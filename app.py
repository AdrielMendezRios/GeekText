from flask import Flask, url_for, redirect, render_template, request
from flask_migrate import Migrate
from models import db, Book, Author
from datetime import datetime

app = Flask(__name__)

isAdmin = True  # just in the mean time...

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

migrate = Migrate(app, db)

db.init_app(app)

@app.route("/")
def home():
    db.session.rollback(); # helpfull when db breaks ( aka when i break it)
    books = db.session.query(Book).all()
    return render_template("index.html", books=books)


"""
    Adriels' TODOs:
    Book Details 
    [~]  An administrator must be able to create a book with the book ISBN, book
        name, book description, price, author, genre, publisher, year published and
        copies sold.
    []  Must be able retrieve a book's detail
    [~] An administrator must be able to create an author with first name, 
        last name, biography and publisher
    []  Must be able to retrieve a list of books associate with an author
"""

@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if isAdmin:
        # check if route being called as a POST Method
        if request.method == 'POST':
            title = request.form.get("title")
            isbn = request.form.get("isbn")
            price = request.form.get("price")
            publisher = request.form.get("publisher")
            genre = request.form.get("genre")
            date_published = datetime.strptime(request.form.get("date_published"), "%Y-%m-%d")
            description = request.form.get("description")
            copies_sold = 0
            author_fname = request.form.get("author_fname")
            author_lname = request.form.get("author_lname")
            author = get_author(author_fname, author_lname)
            author_id = None
            if author is None:
                # create new Author if author not in db
                new_author = Author(first_name=author_fname, last_name=author_lname)
                db.session.add(new_author)
                db.session.commit()
                author_id = new_author.id
            else:
                # retrive id of existing author
                author_id = author.id
            # create Book object and add all the info collected form request.form
            new_book = Book(title=title, isbn=isbn, author_id=author_id, price=price,
                            copies_sold=copies_sold, description=description, genre=genre,
                            publisher=publisher, date_published=date_published)
            # add 'new_book' to db
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for("home"))
        else: # when route is being called normally
            return render_template('add_book.html')
    return redirect(url_for("home")) # when user not an admin (not implemented yet)

# helper function. queries db for author, returns author or empty query object
def get_author(fname, lname):
    author = Author.query.filter_by(first_name=fname, last_name=lname).first()
    return author

@app.route("/add_author", methods=['GET', 'POST'])
def add_author(fname=None, lname=None):
    if isAdmin:
        new_author = Author(first_name=fname, last_name=lname)
        db.session.add(new_author)
        db.session.commit()
    


if __name__ == "__main__":
    app.run()