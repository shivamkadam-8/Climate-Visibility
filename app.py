from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
from src.pipeline.prediction_pipeline import PredictionPipeline
from src.logger import logging as lg


# ----------------------------------------
# App Config
# ----------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise ValueError("❌ SECRET_KEY not found in .env file")

bcrypt = Bcrypt(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


# ----------------------------------------
# MongoDB Connection
# ----------------------------------------

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in .env file")

client = MongoClient(MONGO_URI)
db = client["visibility"]

contact_collection = db["contacts"]
users_collection = db["users"]

lg.info("✅ MongoDB connected successfully")


# ----------------------------------------
# PUBLIC ROUTES
# ----------------------------------------

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        contact_collection.insert_one({
            "name": name,
            "email": email,
            "message": message,
            "created_at": datetime.utcnow()
        })

        flash("Message sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# ----------------------------------------
# AUTH ROUTES
# ----------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if users_collection.find_one({"email": email}):
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        })

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user"] = user["name"]
            session["email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("landing"))


# ----------------------------------------
# PROTECTED ROUTES
# ----------------------------------------

@app.route("/home")
def home():
    if "user" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    return render_template("home.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    prediction = None

    if request.method == "POST":
        try:
            pipeline = PredictionPipeline(request)
            prediction = pipeline.run_pipeline()

            # ✅ Render result.html instead of predict.html
            return render_template("result.html", prediction=prediction)

        except Exception as e:
            lg.error(str(e))
            flash("Prediction failed!", "danger")
            return redirect(url_for("predict"))

    return render_template("predict.html")


# ----------------------------------------
# PASSWORD RESET
# ----------------------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = users_collection.find_one({"email": email})

        if user:
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_url = url_for("reset_password", token=token, _external=True)

            return render_template("forgot_password.html", reset_link=reset_url)
        else:
            flash("Email not found!", "danger")

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            salt="password-reset-salt",
            max_age=600
        )
    except:
        flash("Reset link is invalid or expired!", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )

        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


# ----------------------------------------
# RUN SERVER
# ----------------------------------------

if __name__ == "__main__":
    lg.info("🚀 Starting Flask server...")
    lg.info("👉 Open in browser: http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001, debug=True, use_reloader=False)
