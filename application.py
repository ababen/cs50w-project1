import os, requests
import json

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password": password})
        db.commit()
        session["user_name"] = username
        return render_template("search.html")

@app.route("/login", methods=["POST"])
def login():
    message = None
    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
    # Make sure the login exists.
    if db.execute("SELECT * FROM users WHERE (username = :username) AND (password = :password)",
                {"username": username, "password": password}).rowcount == 1:
        session["user_name"] = username #Store user id here
        session["logged_in"] = True
        return render_template("search.html", username=username)
    else:
        return render_template("error.html", message="Wrong username and password!")


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
    # table = meta.tables['books']

    title = request.form.get("title")
    author = request.form.get("author")
    isbn = request.form.get("isbn")

    if len(title) == 0:
        title = None
    if len(author) == 0:
        author = None
    if len(isbn) == 0:
        isbn = None

    # result = db.execute("SELECT * FROM books WHERE (:title IS NULL OR title LIKE :title) OR (:author IS NULL OR author LIKE :author),{"title": title, "author": author}).fetchall()

    books = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title" : title}).fetchall()

    return render_template("books.html", books=books)

@app.route("/users")
def users():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html", users=users)

@app.route("/book/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    else:
        key = "9n1OXNaooCGd4OuxsOKo2g"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": book.isbn})

        if res.status_code != 200:
            return render_template("error.html", message="404 Error")

        book_all = res.json()
        book_rating = book_all['books'][0]['average_rating']

        reviews = db.execute("SELECT * FROM reviews LEFT JOIN public.users ON (reviews.user_id = users.id) WHERE book_id = :id", {"id": book_id}).fetchall()

        return render_template("book.html", book=book, book_rating=book_rating, reviews=reviews)

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
    stars = request.form.get("stars")
    review = request.form.get("review")
    username = session["user_name"]

    users = db.execute("SELECT username, id from users WHERE username = :username", {"username" : username}).fetchone

    """
    if db.execute("SELECT * FROM reviews LEFT JOIN public.users ON (reviews.user_id = users.id) WHERE book_id = :id AND username = :username", {"id": book_id, "username": username}).rowcount > 0:
        return render_template("error.html", message="Review already exists.")
    else:
        db.execute("INSERT INTO reviews (book_id, user_id, stars, review) VALUES (:book_id, :user_id, :stars, :review)", {"book_id": book_id, "user_id": session["user_id"], "stars": stars, "review": review})
        db.commit()
    """
    return render_template("error.html", message=users.id)

@app.route("/api/<int:isbn_id>", methods=["GET"])
def api(isbn_id):
    key = "9n1OXNaooCGd4OuxsOKo2g"
    res1 = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn_id})

    a = res1.json()
    # b = a['books']
    b = "ty"

    return b

    # if res.status_code != 200:
    #    return(res.status_code)


"""
@app.route("/list", methods=["POST", "GET"])
def list():
    if db.execute("SELECT * FROM books").rowcount == 0:
        return render_template("error.html", message="No books in database.")
    else:
        books = db.execute("SELECT * FROM books").fetchall()
        return render_template("listbooks.html", books=books)
"""
