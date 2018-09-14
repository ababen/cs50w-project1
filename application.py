import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy import and_
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

@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = username").rowcount == 0:
        return render_template("error.html", message="Username already exists.")
    else:
        users = db.execute("SELECT * FROM users")
        return render_template("register.html", users=users)


@app.route("/login", methods=["POST"])
def login():

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
##    try:
##        flight_id = int(request.form.get("flight_id"))
##    except ValueError:
##        return render_template("error.html", message="Invalid flight number.")

    # Make sure the login exists.
    if db.execute("SELECT * FROM users WHERE (username = username) AND (password = password)").rowcount == 0:
        return render_template("error.html", message="No such username and password combination exists.")
    else:
        session["user_id"] = username #Store user id here
        return render_template("welcome.html", username=username)

@app.route("/logout", methods=["GET"])
def logout():
    username = ""
    password = ""
    return render_template("index.html")

@app.route("/list", methods=["POST", "GET"])
def list():
    if db.execute("SELECT * FROM books").rowcount == 0:
        return render_template("error.html", message="No books in database.")
    else:
        books = db.execute("SELECT * FROM books").fetchall()
        return render_template("listbooks.html", books=books)

@app.route("/search", methods=["GET"])
def search():

    return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
#    if db.execute("SELECT * FROM books").rowcount == 0:
#        return render_template("error.html", message="No books in database.")
#    else:
#        books = db.execute("SELECT * FROM books").fetchall()
#        return render_template("books.html", books=books)

    title = ""
    author = ""
    isbn = ""
    array = []

    title = request.form.get("title")
    author = request.form.get("author")
    isbn = request.form.get("isbn")

    if request.form.get("title") is None:
        result = "Empty"
    else:
        result = "Not Empty"

    return render_template("test.html", result=result)
    """
    if author is not None:
        array.append("author LIKE "+author)

    if isbn is not None:
        array.append("ISBN LIKE "+isbn)
    """
    #query = db.execute("SELECT * FROM books").fetchall()


#    if db.execute("SELECT * FROM books WHERE title = :title", {"title": title}).rowcount == 0:
#        return render_template("error.html", message="No such book(s) in database.")
#    else:
#        books = db.execute("SELECT * FROM books WHERE (title = :title OR author = :author OR isbn = :isbn", {"title": title, "author": author, "isbn": isbn}).fetchall()
#        return render_template("books.html", books=books)

@app.route("/book/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    else:
        return render_template("book.html", book=book)
"""
    # Get all books.
    books = db.execute("SELECT name FROM books WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()
    return render_template("book.html", book=book, books=books)
"""
