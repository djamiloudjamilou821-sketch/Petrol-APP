from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from models import db, User
import cloudinary
import cloudinary.uploader


# ADMIN PASSWORD
ADMIN_PASSWORD = "mydjamilou1"


def register_auth(app):

    # =========================
    # REGISTER
    # =========================
    @app.route("/register", methods=["GET", "POST"])
    def register():

        error = None

        if request.method == "POST":

            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            # CHECK IF USER EXISTS
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                error = "Email already exists"

            else:

                hashed_password = generate_password_hash(password)

                new_user = User(
                    username=username,
                    email=email,
                    password=hashed_password
                )

                db.session.add(new_user)
                db.session.commit()

                # LOGIN AUTOMATICALLY
                session.permanent = True
                session["logged_in"] = True
                session["user_id"] = new_user.id
                session["username"] = new_user.username

                return redirect("/home")

        return render_template("register.html", error=error)

    # =========================
    # LOGIN
    # =========================
    @app.route("/login", methods=["GET", "POST"])
    def login():

        error = None

        if request.method == "POST":

            try:
                email = request.form["email"]
                password = request.form["password"]

                user = User.query.filter_by(email=email).first()

                if user and check_password_hash(user.password, password):

                    session.permanent = True
                    session["logged_in"] = True
                    session["user_id"] = user.id
                    session["username"] = user.username

                    return redirect("/home")

                else:
                    error = "Invalid email or password"

            except Exception as e:
                print("DATABASE ERROR:", e)
                error = "Server error. Try again."

        return render_template("login.html", error=error)
    # =========================
    # LOGOUT
    # =========================
    @app.route("/logout")
    def logout():

        session.clear()

        return redirect("/login")

    # =========================
    # ADMIN LOGIN
    # =========================
    @app.route("/admin-login", methods=["GET", "POST"])
    def admin_login():

        error = None

        if request.method == "POST":

            password = request.form["password"]

            if password == ADMIN_PASSWORD:

                session["admin"] = True

                return redirect("/admin")

            else:
                error = "Wrong password"

        return render_template("admin/login.html", error=error)

    # profile
    @app.route("/profile")
    def profile():

        if "user_id" not in session:
            return redirect("/login")

        user = User.query.get(session["user_id"])

        return render_template(
            "profile.html",
            user=user
        )

    @app.route("/edit-profile", methods=["GET", "POST"])
    def edit_profile():

        if "user_id" not in session:
            return redirect("/login")

        user = User.query.get(session["user_id"])

        if request.method == "POST":

            user.username = request.form["username"]
            user.bio = request.form["bio"]
            user.country = request.form["country"]
            user.university = request.form["university"]
            user.petroleum_level = request.form["petroleum_level"]

            file = request.files.get("profile_pic")

            if file and file.filename != "":

                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="petroapp_profiles"
                )

                # ✅ FIX: correct field
                user.profile_pic = upload_result.get("secure_url")

            db.session.commit()

            session["username"] = user.username

            return redirect("/profile")

        return render_template("edit_profile.html", user=user)