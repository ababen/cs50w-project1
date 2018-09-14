import os

from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, or_
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
meta = MetaData(engine,reflect=True)

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
        session["user_id"] = username
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
        session["user_id"] = username #Store user id here
        session["logged_in"] = True
        return render_template("search.html", username=username)
    else:
        return render_template("error.html", message="Wrong username and password!")

@app.route("/logout")
def logout():
    username = None
    password = None
    session["user_id"] = None
    session['logged_in'] = False
    session.clear()
    return render_template("index.html")

@app.route("/list", methods=["POST", "GET"])
def list():
    if db.execute("SELECT * FROM books").rowcount == 0:
        return render_template("error.html", message="No books in database.")
    else:
        books = db.execute("SELECT * FROM books").fetchall()
        return render_template("listbooks.html", books=books)

# Is this route even needed?
@app.route("/search", methods=["GET"])
def search():
    if not session.get('logged_in'):
        return render_template("error.html", message="You are not logged in!")
    else:
        return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
    table = meta.tables['books']
#    if db.execute("SELECT * FROM books").rowcount == 0:
#        return render_template("error.html", message="No books in database.")
#    else:
#        books = db.execute("SELECT * FROM books").fetchall()
#        return render_template("books.html", books=books)
    title = request.form.get("title")
    author = request.form.get("author")
    isbn = request.form.get("isbn")

    query = []

    if len(title) > 0:
        query.append('title LIKE title')
    if len(author) > 0:
        query.append("author LIKE :author")
    if len(isbn) > 0:
        query.append("isbn LIKE :isbn")

    # select_all = select([table]).where(or_(query))
    # result = db.execute(select_all)

    # result = db.execute("SELECT * FROM books WHERE :query", {"query": query}).fetchall()
    result = query
    return render_template("test.html", result=result)
    # query = db.execute("SELECT * FROM books").fetchall()


#    if db.execute("SELECT * FROM books WHERE title = :title", {"title": title}).rowcount == 0:
#        return render_template("error.html", message="No such book(s) in database.")
#    else:
#        books = db.execute("SELECT * FROM books WHERE (title = :title OR author = :author OR isbn = :isbn", {"title": title, "author": author, "isbn": isbn}).fetchall()
#        return render_template("books.html", books=books)

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
        return render_template("book.html", book=book)
    """
    # Get all books.
    books = db.execute("SELECT name FROM books WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()
    return render_template("book.html", book=book, books=books)
    """
