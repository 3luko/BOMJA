from flask import Flask, render_template, request, redirect, session, url_for
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from pathlib import Path
import os
import json


#SETUP
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, override=True)



UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
JSON_FILE = BASE_DIR / "static" / "data" / "events.json"

#Creating Flask app and Bcrypt instance
app = Flask(__name__)
# Enable Bcrypt
bcrypt = Bcrypt(app)

#Env variables
app.secret_key = os.getenv("SECRET_KEY")
MYPASS = os.getenv("ADMIN_PASSWORD_HASH")


print("http://127.0.0.1:5000")

  


#Route for home page
@app.route("/")
def home():
    print("Login page opened", flush=True)
    return render_template("bomja1.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    # If the user is submitting the login form
    if request.method == "POST":

        password = request.form.get("password")

        if not password:
            print("Password is required", flush=True)
            return "Password is required", 400

        # Check the password
        if MYPASS == password:
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

    events_file = BASE_DIR / "static" / "data" / "events.json"
    with open(events_file, "r", encoding="utf-8") as file:
        events = json.load(file)

    return render_template("dashboard.html", events=events)


#ROute for image upload
@app.route("/admin/upload", methods=["POST"])
def upload_image():

    # Get the uploaded file
    file = request.files["image"]

    # Get the alt text from the form
    alt_text = request.form["alt"]

    # Save the actual image
    file.save(UPLOAD_FOLDER / file.filename)

    # Add image information to JSON
    add_image_to_json(
        file.filename,
        alt_text
    )

    return redirect(url_for("dashboard"))



#FUNCTION for adding image information to JSON
def add_image_to_json(filename, alt_text):
    # Open the existing JSON file
    with open(JSON_FILE, "r") as file:
        images = json.load(file)

    # Add the new image to the list
    images.append({
        "image": filename,
        "alt": alt_text
    })

    # Write the updated list back to the JSON file
    with open(JSON_FILE, "w") as file:
        json.dump(images, file, indent=4)


@app.route("/admin/delete/<filename>", methods=["POST"])
def delete_image(filename):
    # Remove the image from the JSON file
    remove_image_from_json(filename)

    # Remove the actual image file
    image_path = UPLOAD_FOLDER / filename
    if image_path.exists():
        image_path.unlink()

    return redirect(url_for("dashboard"))   

def remove_image_from_json(filename):
    # Open the existing JSON file
    with open(JSON_FILE, "r") as file:
        images = json.load(file)

    # Remove the image with the specified filename
    images = [img for img in images if img["image"] != filename]

    # Write the updated list back to the JSON file
    with open(JSON_FILE, "w") as file:
        json.dump(images, file, indent=4)


#Route for logoout page
@app.route("/logout")
def logout():
    session.clear()
    print("Admin logged out", flush=True)

    return redirect("../bomja1.html")


if __name__ == "__main__":
    app.run(debug=True)