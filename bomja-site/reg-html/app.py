from flask import Flask, send_from_directory, render_template, request, redirect, session, url_for, abort
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import os
import sqlite3
import uuid



# Database connection function
def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection

# Initialize the database if it doesn't exist
def init_db():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            event_ticket_link TEXT,
            alt TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE if NOT EXISTS pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)


    connection.commit()
    connection.close()

def init_admin():
    connection = get_db_connection()

    existing_admin = connection.execute(
        "SELECT id from pass LIMIT 1"
    ).fetchone()

    if existing_admin:
        connection.close()
        return 

    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not password:
        connection.close()
        raise RuntimeError(
            "ADMIN_USERNAME and ADMIN_PASSWORD are required "
            "to create the initial administrator."
        )

    connection.execute(
        """
        INSERT INTO pass (username, password)
        VALUES (?,?)
        """,
        (username, password)
    )

    connection.commit()
    connection.close()

    print("Initial administrator creator")
    


#SETUP

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, override=True)
DATABASE = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "bomja.db"))
DATABASE.parent.mkdir(parents=True, exist_ok=True)

init_db()
init_admin()

UPLOAD_FOLDER = Path(
    os.getenv(
        "UPLOAD_FOLDER",
        BASE_DIR / "static" / "uploads"
    )
)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return(
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

#Creating Flask app and Bcrypt instance
app = Flask(__name__, template_folder="templates", static_folder="static")

app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is required."
    )

csrf = CSRFProtect(app)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limit upload size to 16MB

IS_PRODUCTION = os.getenv("FLASK_ENV") == "production"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    SESSION_COOKIE_SAMESITE="Lax"
)


if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required")


print("http://127.0.0.1:5000")

  


#Route for home page
@app.route("/")
def home():
    print("Home page opened", flush=True)

    connection = get_db_connection()

    # Get all events from database
    events = connection.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    connection.close()

    return render_template("bomja1.html",
                           events=events)


# Route for logging in.
@app.route("/login", methods=["GET", "POST"])
def login():

    # If the user is submitting the login form
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not password or not username:
            print("Password is required", flush=True)
            return "Password is required", 400

        connection = get_db_connection()
        admin = connection.execute(
            """
                SELECT username, password
                FROM pass
                ORDER BY id DESC
                LIMIT 1
            """
        ).fetchone()

        connection.close()
         
        if not admin:
            app.logger.error("No administrator account found.")
            return "Administrator account unavailable", 500

        username_correct = username == admin["username"]

        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            admin["password"].encode("utf-8")
        )



        if username_correct and password_correct:
            print("Correct username and password", flush=True)

            session.clear()
            session["admin"] = True

            return redirect(url_for("dashboard"))

        else:
            print("Wrong password or Wrong Username", flush=True)
            
            return "Wrong password or Wrong Username", 401

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


# Route to get to the mailing list page (NOT READY)
@app.route("/mail-list", methods=["GET", "POST"])
def mail_list():
    print("Mail List not yet ready.", flush=True)

    return render_template("mail-list.html")

# Route for the Tickets tab
@app.route("/tickets")
def ticket():
    return render_template("tickets.html")


#ROute for image upload

@app.route("/admin/upload", methods=["POST"])
def upload_image():
    if not session.get("admin"):
        print("No admin session", flush=True)
        abort(403)  # Forbidden


    file = request.files.get("image")
    filename = request.form.get("alt", "").strip()

    if not file or not file.filename:
        return "No image selected", 400

    if not allowed_file(file.filename):
        return "Invalid image type", 400

    filename = secure_filename(file.filename)

    #Preventing 2 uploads from having the same filename
    filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Save the file to the uploads folder
    file.save(UPLOAD_FOLDER / filename)

    ticket_link = request.form.get("ticketLink", "").strip()
    if ticket_link and not ticket_link.startswith(("http://", "https://")):
        return "Ticket link must start with http:// or https://", 400

    add_event(
        filename, 
        request.form["alt"], 
        ticket_link
    )


    return redirect(url_for("dashboard"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

#Route for image deletion
@app.route("/admin/delete/<filename>", methods=["POST"])
def delete_image(filename):

    if not session.get("admin"):
        print("No admin session for deletion", flush=True)
        abort(403)  # Forbidden

    remove_event(filename)

    return redirect(url_for("dashboard")) 

#Route for logoout page
@app.route("/logout")
def logout():
    session.clear()
    print("Admin logged out", flush=True)

    return redirect(url_for("home"))  


# Function to add an event to the database
def add_event(image, alt, event_ticket_link):

    connection = get_db_connection()

    existing = connection.execute(
        "SELECT 1 FROM events WHERE image = ?",
        (image,)
    ).fetchone()

    

    if not existing:
        connection.execute(
            """
            INSERT INTO events (image, alt, event_ticket_link)
            VALUES (?, ?, ?)
            """,
            (image, alt, event_ticket_link)
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

    file_path = UPLOAD_FOLDER / image

    if file_path.exists():
        file_path.unlink()
        print(f"Deleted file: {file_path}", flush=True)


if __name__ == "__main__":
    app.run(debug=True)