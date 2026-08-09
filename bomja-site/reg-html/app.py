from flask import Flask, render_template, request, redirect, session, url_for
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from pathlib import Path
import os


#SETUP
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)
UPLOAD_FOLDER = BASE_DIR.parent / "assets"

#Creating Flask app and Bcrypt instance
app = Flask(__name__)
# Enable Bcrypt
bcrypt = Bcrypt(app)

#Env variables
app.secret_key = os.getenv("SECRET_KEY")
PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
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

        print("Password entered:", password)

        # Check the password
        if bcrypt.check_password_hash(PASSWORD_HASH, password):
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

    return render_template("dashboard.html")


#Route for logoout page
@app.route("/logout")
def logout():
    session.clear()
    print("Admin logged out", flush=True)

    return redirect("../bomja1.html")


if __name__ == "__main__":
    app.run(debug=True)