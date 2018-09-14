import os

from flask import Flask, session, render_template
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

"""
@app.route("/", methods=["POST"])
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
    else
        return render_template("index.html")
"""
