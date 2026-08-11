from flask import Flask, render_template, request, redirect, session, url_for
from dotenv import load_dotenv
from pathlib import Path
import os
import sqlite3


#SETUP
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DATABASE = BASE_DIR / "static" / "data" / "bomja.db"
load_dotenv(ENV_PATH, override=True)



UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


#Creating Flask app and Bcrypt instance
app = Flask(__name__, template_folder="templates", static_folder="static")

#Env variables
app.secret_key = os.getenv("SECRET_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD_HASH")


print("http://127.0.0.1:5000")

  


#Route for home page
@app.route("/")
def home():
    print("Home page opened", flush=True)

    connection = get_db_connection()

    # Get all events from database
    events = connection.execute("SELECT * FROM events ORDER BY id DESC").fetchall()

    return render_template("bomja1.html",
                           events=events)



@app.route("/login", methods=["GET", "POST"])
def login():

    # If the user is submitting the login form
    if request.method == "POST":

        password = request.form.get("password")

        if not password:
            print("Password is required", flush=True)
            return "Password is required", 400

        # Check the password
        if ADMIN_PASSWORD and password == ADMIN_PASSWORD:
            print("Correct password", flush=True)

            session.clear()
            session["admin"] = True

            return redirect(url_for("dashboard"))

        else:
            print("Wrong password", flush=True)
            return "Wrong password", 401

    # If the user is simply visiting /login
    return render_template("login.html")


#Route for dashboard page (Admin) 
@app.route("/dashboard")
def dashboard():
    print("Dashboard route reached", flush=True)

    if not session.get("admin"):
        print("No admin session", flush=True)
        return redirect(url_for("home"))

    connection = get_db_connection()
    events = connection.execute("SELECT * FROM events").fetchall()
    connection.close()

    return render_template("dashboard.html", events=events)


#ROute for image upload
@app.route("/admin/upload", methods=["POST"])
def upload_image():

    file = request.files["image"]
    filename = file.filename

    # Save the file to the uploads folder
    file.save(UPLOAD_FOLDER / filename)

    add_event(filename, request.form["alt"])


    return redirect(url_for("dashboard"))



@app.route("/admin/delete/<filename>", methods=["POST"])
def delete_image(filename):

    remove_event(filename)

    return redirect(url_for("dashboard")) 

#Route for logoout page
@app.route("/logout")
def logout():
    session.clear()
    print("Admin logged out", flush=True)

    return redirect(url_for("home"))  


# Initialize the database if it doesn't exist
def init_db():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            image TEXT NOT NULL,

            alt TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()

# Database connection function
def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# Function to add an event to the database
def add_event(image, alt):

    connection = get_db_connection()

    existing = connection.execute(
        "SELECT 1 FROM events WHERE image = ?",
        (image,)
    ).fetchone()

    if not existing:
        connection.execute(
            """
            INSERT INTO events (image, alt)
            VALUES (?, ?)
            """,
            (image, alt)
        )
        connection.commit()

    connection.close()

# Function to remove an event from the database
def remove_event(image):
    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM events
        WHERE image = ?
        """,
        (image,)
    )

    connection.commit()

    connection.close()



if __name__ == "__main__":
    init_db()
    app.run(debug=True)