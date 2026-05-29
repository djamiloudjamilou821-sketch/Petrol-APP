from flask import Flask, render_template, request, redirect, session
from database import db
from models import Lesson, Formula
from datetime import timedelta

from lessons import register_lessons
from quiz import register_quiz
from formulas import register_formulas
from converter import register_converter
from admin import register_admin
from auth import register_auth
import os

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=365)

app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.secret_key = "secret123"

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.qmwbvuspqepsmhirdgqk:C,s-L7Q47st?2M,@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# REGISTER ROUTES
register_lessons(app)
register_quiz(app)
register_formulas(app)
register_converter(app)
register_admin(app)
register_auth(app)

# 🏠 HOME PAGE
@app.route("/home")
def home():

    if not session.get("logged_in"):
        return redirect("/login")

    lang = session.get("lang", "en")

    return render_template("index.html", lang=lang)


# 🛢️ POROSITY CALCULATOR
@app.route("/porosity", methods=["GET", "POST"])
def porosity():
    result = None

    if request.method == "POST":
        vp = request.form.get("vp")
        vt = request.form.get("vt")

        if vp and vt:
            vp = float(vp)
            vt = float(vt)

            if vt != 0:
                result = round((vp / vt) * 100, 2)
            else:
                result = "Error: Total volume cannot be zero"

    return render_template("porosity.html", result=result)


# LANGUAGE
@app.route("/", methods=["GET", "POST"])
def language():
    # If user selects manually
    if request.method == "POST":
        lang = request.form.get("lang")
        session["lang"] = lang
        return redirect("/home")

    # If already selected before
    if "lang" in session:
        return redirect("/home")

    # AUTO DETECT LANGUAGE
    browser_lang = request.headers.get("Accept-Language")

    if browser_lang:
        if browser_lang.startswith("fr"):
            session["lang"] = "fr"
        else:
            session["lang"] = "en"
    else:
        session["lang"] = "en"

    return render_template("language.html")
# ▶️ RUN APP
if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
