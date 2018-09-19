import os, requests
import json

from flask import Flask, session, render_template, request, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
from getgoodreads import get_goodreads

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    username = None
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username",
                {"username": username}).rowcount > 0:
        return render_template("error.html", message="Username already exists.")
    else:
        password1 = sha256_crypt.encrypt(password)
        password2 = sha256_crypt.encrypt(password1)

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password": password2})
        db.commit()
        session["user_name"] = username
        return render_template("search.html")

        """
        me = User('John Doe', 'default')
        me.pw_hash
        'sha1$Z9wtkQam$7e6e814998ab3de2b63401a58063c79d92865d79'
        me.check_password('default')
        True
        me.check_password('defaultx')
        False
        """

@app.route("/login", methods=["POST"])
def login():
    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure the login exists.
    hash = db.execute("SELECT password FROM users WHERE username = :username", {"username" : username}).fetchone()
    
    if db.execute("SELECT * FROM users WHERE (username = :username) AND (password = :password))",
                {"username": username, "password": sha256_crypt.verify(hash.password[0], password)}).rowcount == 1:
        session["user_name"] = username #Store user id here
        session["logged_in"] = True
        return render_template("search.html", username=username)
    else:
        return render_template("error.html", message="Wrong username and/or password!")

@app.route("/logout")
def logout():
    username = None
    password = None
    session["user_name"] = None
    session['logged_in'] = False
    session.clear()
    return render_template("index.html")

# Is this route even needed?
@app.route("/search", methods=["GET"])
def search():
    if not session.get('logged_in'):
        return render_template("error.html", message="You are not logged in!")
    else:
        return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
    searchqry = request.form.get("searchqry")

    if len(searchqry) == 0:
        searchqry = None

    books = db.execute("SELECT * FROM books WHERE (title LIKE :searchqry) OR (author LIKE :searchqry) OR (isbn LIKE :searchqry)",
                {"searchqry" : '%' + searchqry + '%'}).fetchall()

    return render_template("books.html", books=books)

@app.route("/book/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    else:
        goodreads = get_goodreads(book.isbn)

        if goodreads.status_code != 200:
            return render_template("error.html", message="404 Error")

        book_all = goodreads.json()
        book_rating = book_all['books'][0]['average_rating']

        reviews = db.execute("SELECT * FROM reviews LEFT JOIN public.users ON (reviews.user_id = users.id) WHERE book_id = :id", {"id": book_id}).fetchall()

        return render_template("book.html", book=book, book_rating=book_rating, reviews=reviews)

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
    stars = request.form.get("stars")
    review = request.form.get("review")
    username = session["user_name"]

    users = db.execute("SELECT username, id from users WHERE username = :username", {"username" : username}).fetchone()


    if db.execute("SELECT * FROM reviews LEFT JOIN public.users ON (reviews.user_id = users.id) WHERE book_id = :id AND username = :username", {"id": book_id, "username": username}).rowcount > 0:
        return render_template("error.html", message="Review already exists.")
    else:
        db.execute("INSERT INTO reviews (book_id, user_id, stars, review) VALUES (:book_id, :user_id, :stars, :review)", {"book_id": book_id, "user_id": users.id, "stars": stars, "review": review})
        db.commit()

    return render_template("error.html", message="Review added")

@app.route("/api/<isbn_id>", methods=["GET"])
def api(isbn_id):
    book_api = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn" : isbn_id}).fetchone()

    if book_api is None:
        goodreads = get_goodreads(isbn_id)
        if goodreads.status_code != 200:
            return abort(404)
        else:
            book_api = goodreads.json()
            return book_api
    else:
        book_reviews = db.execute("SELECT COUNT(id), AVG(stars) FROM reviews WHERE book_id = :book_id", {"book_id" : book_api.id}).fetchone()

    resp = {}
    resp['title'] = book_api.title
    resp['author'] = book_api.author
    resp['year'] = book_api.year
    resp['isbn'] = book_api.isbn
    try:
        resp['review_count'] = str(book_reviews[0])
        resp['average_score'] = '% 1.1f' % book_reviews[1]
    except TypeError:
        resp['review_count'] = "Not enough reviews"
        resp['average_score'] = "Not enough reviews"

    json_resp = json.dumps(resp)

    return json_resp, 200
