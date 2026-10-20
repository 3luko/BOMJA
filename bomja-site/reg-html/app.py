from flask import Flask, flash, send_from_directory, render_template, request, redirect, session, url_for, abort
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import os
import sqlite3
import uuid
from collections import defaultdict



# Database connection function
def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection

# Initialize the database if it doesn't exist
def init_db():

    connection = get_db_connection()
    # events table (event flyers)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            event_ticket_link TEXT,
            alt TEXT NOT NULL,
            is_visible INTEGER NOT NULL DEFAULT 1
        )
    """)
    event_columns = connection.execute("PRAGMA table_info(events)").fetchall()
    if not any(column[1] == "is_visible" for column in event_columns):
        connection.execute(
            "ALTER TABLE events ADD COLUMN is_visible INTEGER NOT NULL DEFAULT 1"
        )
    # Password table
    connection.execute("""
        CREATE TABLE if NOT EXISTS pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS gallery_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            alt_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS slideshow_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            alt_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS site_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    slideshow_count = connection.execute(
        "SELECT COUNT(*) FROM slideshow_photos"
    ).fetchone()[0]
    if slideshow_count == 0:
        connection.executemany(
            """
            INSERT INTO slideshow_photos (filename, alt_text)
            VALUES (?, ?)
            """,
            [
                ("visuals/BOMJA001-21.png", "BOMJA event image"),
                ("visuals/BOMJA002-93.png", "BOMJA event image"),
                ("visuals/BOMJA001-40.png", "BOMJA event image"),
                ("visuals/BOMJA001-43.png", "BOMJA event image"),
            ]
        )

    default_ticket_url = "https://linktr.ee/bomja?utm_source=ig&utm_medium=social&utm_content=link_in_bio&fbclid=PAcGRvZgJleHRuA2FlbQIxMQBzcnRjBmFwcF9pZA85MzY2MTk3NDMzOTI0NTkAAac6331DnS-VMpZp-ChK1-P46oWhYBzeVTqMYaWlmAJZQw0vWiWiERGP4wP8HQ_aem_MSE-sSSs678j71U3RAZjPA"
    existing_ticket_setting = connection.execute(
        "SELECT value FROM site_settings WHERE key = 'tickets_url'"
    ).fetchone()
    if not existing_ticket_setting:
        connection.execute(
            "INSERT INTO site_settings (key, value) VALUES (?, ?)",
            ("tickets_url", default_ticket_url)
        )

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

EVENTS_FOLDER = Path(
    os.getenv(
        "EVENTS_FOLDER",
        BASE_DIR / "static" / "uploads" / "events"
    )
)

GALLERY_FOLDER = Path(
    os.getenv(
        "GALLERY_FOLDER",
        BASE_DIR / "static" / "uploads" / "gallery"
    )
)

SLIDESHOW_FOLDER = Path(
    os.getenv(
        "SLIDESHOW_FOLDER",
        BASE_DIR / "static" / "uploads" / "slideshow"
    )
)


EVENTS_FOLDER.mkdir(parents=True, exist_ok=True)
GALLERY_FOLDER.mkdir(parents=True, exist_ok=True)
SLIDESHOW_FOLDER.mkdir(parents=True, exist_ok=True)


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

app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024  # Limit upload size to 16MB

IS_PRODUCTION = os.getenv("FLASK_ENV") == "production"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    SESSION_COOKIE_SAMESITE="Lax"
)


if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required")


print("http://127.0.0.1:5000")

  


def get_site_setting(key, default=""):
    connection = get_db_connection()
    row = connection.execute(
        "SELECT value FROM site_settings WHERE key = ?",
        (key,)
    ).fetchone()
    connection.close()
    return row["value"] if row else default

#Route for home page
@app.route("/")
def home():
    print("Home page opened", flush=True)

    connection = get_db_connection()

    # Get currently visible upcoming events.
    events = connection.execute(
        "SELECT * FROM events WHERE is_visible = 1 ORDER BY id DESC"
    ).fetchall()

    # Show past event flyers only when the event has gallery photos.
    gallery_events = connection.execute("""
        SELECT events.*
        FROM events
        WHERE events.is_visible = 0
          AND EXISTS (
              SELECT 1
              FROM gallery_photos
              WHERE gallery_photos.event_id = events.id
          )
        ORDER BY events.id DESC
    """).fetchall()

    slideshow_photos = connection.execute("""
        SELECT id, filename, alt_text
        FROM slideshow_photos
        ORDER BY id ASC
    """).fetchall()

    tickets_url = get_site_setting("tickets_url", "https://linktr.ee/bomja")

    connection.close()

    return render_template("bomja1.html",
                           events=events,
                           gallery_events=gallery_events,
                           slideshow_photos=slideshow_photos,
                           tickets_url=tickets_url)


@app.route("/gallery/<int:event_id>")
def event_gallery(event_id):
    connection = get_db_connection()
    event = connection.execute("""
        SELECT *
        FROM events
        WHERE id = ? AND is_visible = 0
    """, (event_id,)).fetchone()

    if not event:
        connection.close()
        abort(404)

    photos = connection.execute("""
        SELECT filename, alt_text
        FROM gallery_photos
        WHERE event_id = ?
        ORDER BY created_at ASC, id ASC
    """, (event_id,)).fetchall()
    connection.close()

    if not photos:
        abort(404)

    return render_template("event_gallery.html", event=event, photos=photos)


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
    events = connection.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    gallery_photos = connection.execute("""
    SELECT
        gallery_photos.id,
        gallery_photos.event_id,
        gallery_photos.filename,
        gallery_photos.alt_text,
        events.alt AS event_name
    FROM gallery_photos
    JOIN events
        ON gallery_photos.event_id = events.id
    ORDER BY events.id DESC
""").fetchall()
    slideshow_photos = connection.execute("""
        SELECT id, filename, alt_text
        FROM slideshow_photos
        ORDER BY id ASC
    """).fetchall()

    gallery_by_event = defaultdict(list)

    for photo in gallery_photos:
        gallery_by_event[photo["event_id"]].append(photo)

    connection.close()

    tickets_url = get_site_setting("tickets_url", "https://linktr.ee/bomja")

    return render_template(
        "dashboard.html",
        events=events,
        gallery_by_event=gallery_by_event,
        slideshow_photos=slideshow_photos,
        tickets_url=tickets_url
    )



# Route for the Tickets tab
@app.route("/tickets")
def ticket():
    tickets_url = get_site_setting("tickets_url", "https://linktr.ee/bomja")
    return redirect(tickets_url, code=302)


#ROute for Event upload
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
    
    # Save the file to the events folder
    file.save(EVENTS_FOLDER / filename)

    ticket_link = request.form.get("ticketLink", "").strip()
    if ticket_link and not ticket_link.startswith(("http://", "https://")):
        return "Ticket link must start with http:// or https://", 400

    add_event(
        filename, 
        request.form["alt"], 
        ticket_link
    )


    return redirect(url_for("dashboard"))


# Route for uploading Gallery images related to the event
@app.route("/admin/upload-gallery", methods=["POST"])
def upload_gallery():

    if not session.get("admin"):
        abort(403)
    #Getting event id from the form
    event_id = request.form.get("event_id")
    # Validating that an event id was selected
    if not event_id:
        return "No event selected", 400

    files = request.files.getlist("images")

    if not files:
        return "No images selected", 400

    # Connecting to the database
    connection = get_db_connection()

    for file in files:

        if not file or not file.filename:
            continue

        if not allowed_file(file.filename):
            return "Invalid image type", 400

        filename = secure_filename(file.filename)

        filename = f"{uuid.uuid4().hex}_{filename}"
        # Saving file into the gallery folder
        file.save(GALLERY_FOLDER / filename)
        alt_text = request.form.get("alt", "").strip()

        # Inserting the event id, filename, and alt text (if included)
        connection.execute("""
            INSERT INTO gallery_photos (event_id, filename, alt_text)
            VALUES (?, ?, ?)
        """, (event_id, filename, alt_text))

    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/upload-slideshow", methods=["POST"])
def upload_slideshow():
    if not session.get("admin"):
        abort(403)

    file = request.files.get("image")
    if not file or not file.filename:
        return "No image selected", 400

    if not allowed_file(file.filename):
        return "Invalid image type", 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(SLIDESHOW_FOLDER / filename)

    connection = get_db_connection()
    connection.execute(
        """
        INSERT INTO slideshow_photos (filename, alt_text)
        VALUES (?, ?)
        """,
        (f"uploads/slideshow/{filename}", request.form.get("alt", "").strip())
    )
    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


# route for uploading event flyers
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(EVENTS_FOLDER, filename)

# route for uploading to gallery folder photos
@app.route("/gallery-uploads/<filename>")
def gallery_uploaded_file(filename):
    return send_from_directory(GALLERY_FOLDER, filename)


@app.route("/slideshow-uploads/<path:filename>")
def slideshow_file(filename):
    return send_from_directory(BASE_DIR / "static", filename)

#Route for image deletion
@app.route("/admin/delete/<filename>", methods=["POST"])
def delete_image(filename):

    if not session.get("admin"):
        print("No admin session for deletion", flush=True)
        abort(403)  # Forbidden

    remove_event(filename)

    return redirect(url_for("dashboard")) 

@app.route("/admin/delete-gallery/<filename>", methods=["POST"])
def delete_gallery_image(filename):

    if not session.get("admin"):
        print("No admin session for deletion", flush=True)
        abort(403)

    remove_gallery_image(filename)
    return redirect(url_for("dashboard"))


@app.route("/admin/delete-slideshow/<int:photo_id>", methods=["POST"])
def delete_slideshow(photo_id):
    if not session.get("admin"):
        abort(403)

    connection = get_db_connection()
    photo = connection.execute(
        "SELECT filename FROM slideshow_photos WHERE id = ?",
        (photo_id,)
    ).fetchone()
    if not photo:
        connection.close()
        abort(404)

    connection.execute("DELETE FROM slideshow_photos WHERE id = ?", (photo_id,))
    connection.commit()
    connection.close()

    if photo["filename"].startswith("uploads/slideshow/"):
        (BASE_DIR / "static" / photo["filename"]).unlink(missing_ok=True)

    return redirect(url_for("dashboard"))


@app.route("/admin/update-tickets-link", methods=["POST"])
def update_tickets_link():
    if not session.get("admin"):
        abort(403)

    tickets_url = request.form.get("tickets_url", "").strip()
    if not tickets_url:
        return "Ticket link is required", 400
    if not tickets_url.startswith(("http://", "https://")):
        return "Ticket link must start with http:// or https://", 400

    connection = get_db_connection()
    connection.execute(
        "INSERT INTO site_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        ("tickets_url", tickets_url)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/event/<int:event_id>/visibility", methods=["POST"])
def update_event_visibility(event_id):
    if not session.get("admin"):
        abort(403)

    is_visible = request.form.get("is_visible") == "1"
    connection = get_db_connection()
    connection.execute(
        "UPDATE events SET is_visible = ? WHERE id = ?",
        (int(is_visible), event_id)
    )
    connection.commit()
    connection.close()

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

def remove_event(image):
    connection = get_db_connection()

    # Find the event first
    event = connection.execute(
        """
        SELECT id
        FROM events
        WHERE image = ?
        """,
        (image,)
    ).fetchone()

    if not event:
        connection.close()
        return

    event_id = event["id"]

    # Get all gallery photos connected to this event
    gallery_photos = connection.execute(
        """
        SELECT filename
        FROM gallery_photos
        WHERE event_id = ?
        """,
        (event_id,)
    ).fetchall()

    # Delete gallery database rows first
    connection.execute(
        """
        DELETE FROM gallery_photos
        WHERE event_id = ?
        """,
        (event_id,)
    )

    # Now the event can safely be deleted
    connection.execute(
        """
        DELETE FROM events
        WHERE id = ?
        """,
        (event_id,)
    )

    connection.commit()
    connection.close()

    # Delete associated gallery files
    for photo in gallery_photos:
        gallery_path = GALLERY_FOLDER / photo["filename"]

        if gallery_path.exists():
            gallery_path.unlink()
            print(
                f"Deleted gallery file: {gallery_path}",
                flush=True
            )

    # Delete event flyer
    event_path = EVENTS_FOLDER / image

    if event_path.exists():
        event_path.unlink()
        print(
            f"Deleted event file: {event_path}",
            flush=True
        )

def remove_gallery_image(filename):
    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM gallery_photos
        WHERE filename = ?
        """,
        (filename,)
    )

    connection.commit()

    connection.close()

    file_path = GALLERY_FOLDER / filename


    if file_path.exists():
        file_path.unlink()
        print(f"Deleted file: {file_path}", flush=True)
    else:
        print(f"File does not exist: {file_path}", flush=True)


if __name__ == "__main__":
    app.run(debug=True)