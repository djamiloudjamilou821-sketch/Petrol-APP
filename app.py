from flask import Flask, render_template, request, redirect, session
from database import db
from supabase_client import supabase
from models import Lesson, Formula, User, Post, Comment, Like
from datetime import timedelta
from werkzeug.utils import secure_filename

import requests
from dotenv import load_dotenv
from flask import jsonify
load_dotenv()

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

import uuid

def upload_to_supabase(file):
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    file_bytes = file.read()

    supabase.storage.from_("post-images").upload(
        filename,
        file_bytes,
        {"content-type": file.content_type}
    )

    public_url = supabase.storage.from_("post-images").get_public_url(filename)

    return public_url
# 🏠 HOME PAGE
@app.route("/home")
def home():

    if not session.get("logged_in"):
        return redirect("/login")

    lang = session.get("lang", "en")

    return render_template("index.html", lang=lang)

@app.route("/subject")
def subject_home():

    subjects = [
        {
            "name": "Mathematics",
            "description": "Mathematics is the foundation of petroleum engineering. It is used to calculate flow rates, pressure, porosity, reserves estimation, and reservoir modeling. Without math, it is impossible to design or analyze petroleum systems."
        },
        {
            "name": "Physics",
            "description": "Physics explains how fluids behave underground and in pipelines. It helps engineers understand pressure, flow dynamics, heat transfer, and mechanical behavior of rocks and fluids."
        },
        {
            "name": "Chemistry",
            "description": "Chemistry is essential for understanding the composition of oil, gas, and reservoir fluids. It is used in refining, corrosion control, and understanding reactions between fluids and rocks."
        }
    ]

    return render_template("subject_home.html", subjects=subjects)

@app.route("/subject/<subject_name>")
def subject_index(subject_name):

    lessons = Lesson.query.filter_by(subject=subject_name).all()

    return render_template("subject_index.html",
                           subject=subject_name,
                           lessons=lessons)
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

@app.route("/petroai")
def petroai_page():

    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("petroai.html")

@app.route("/ask_petroai", methods=["POST"])
def ask_petroai():

    question = request.json.get("question")

    # 🧠 INIT MEMORY
    if "chat_history" not in session:
        session["chat_history"] = []

    # =========================
    # ADD USER MESSAGE TO MEMORY
    # =========================

    session["chat_history"].append({
        "role": "user",
        "content": question
    })

    # Keep last 10 messages only
    session["chat_history"] = session["chat_history"][-10:]

    # =========================
    # SYSTEM MESSAGE
    # =========================

    system_message = {
        "role": "system",
        "content": (
            "You are PetroAI, the official assistant of PetroApp, a petroleum engineering learning platform."

            "About PetroApp:"
            "- It teaches petroleum engineering through lessons, quizzes, and calculators"
            "- It helps students understand reservoir engineering, drilling, production, and formulas"
            "- It includes tools like porosity calculator and unit converters"
            "- it was built by Djamilou Harouna Maman nigerien student in Ghana very passionate in Oil and Gaz"
            "- Djamilou was born in Agadez and got SONIDEP's scholarship to study in Ghana in 2025"
            "- SONIDEP is a national oil and gas campany in Niger"

            "Your role:"
            "- Act like a tutor inside the PetroApp system"
            "- Help users understand petroleum engineering clearly"
            "- Guide users through app features when needed"

            "User information:"
            f"The current user is called {session.get('user_name', 'Student')}."

            "Your behavior:"
            "- Always respond in a personal way using the user's name when appropriate"
            "- Be friendly and supportive like a tutor"
            "- Act like you are talking directly to this student"
            "- Help them learn petroleum engineering step by step"


            "Default writing style rules:"
            "- Always answer in clear paragraphs by default"
            "- Do NOT use bullet points unless the user explicitly asks for them"
            "- Do NOT use tables unless requested"
            "- Keep explanations simple, structured, and natural like a teacher speaking"
            "- Maximum 2–5 short paragraphs per answer"
            "- Use bullet points ONLY if the user says: 'use bullets', 'list', or 'steps'"
            "- Make answers easy to read on mobile"
            "- Avoid textbook or report style formatting"
            "- Ask to the user if they need more clarification after answer"
            "- Always write formulas in simple text format, not LaTeX"
            "- Use formats like: V = m/t, φ = Vp/Vt, Q = A × v"
            "- NEVER use fractions like \\frac{}{} or LaTeX math symbols"
            "- Keep formulas readable on mobile screens"
            "- Use plain ASCII math only"
            "- Explain formulas in words below if needed"
        )
    }

    # =========================
    # BUILD MESSAGES
    # =========================

    messages = [system_message] + session["chat_history"]

    # =========================
    # API REQUEST
    # =========================

    headers = {
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": messages
    }

    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    data = response.json()

    answer = data["choices"][0]["message"]["content"]

    # =========================
    # SAVE ASSISTANT RESPONSE
    # =========================

    session["chat_history"].append({
        "role": "assistant",
        "content": answer
    })

    session.modified = True

    return jsonify({"answer": answer})

# COMMUNITY
@app.route("/community")
def community():

    if "user_id" not in session:
        return redirect("/login")

    posts = Post.query.order_by(
        Post.created_at.desc()
    ).all()

    return render_template(
        "community.html",
        posts=posts
    )



ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/create-post", methods=["GET", "POST"])
def create_post():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        content = request.form.get("content")
        file = request.files.get("image")

        image_url = None

        # Upload image to Supabase
        if file and file.filename:

            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file_bytes = file.read()

            supabase.storage.from_("post-images").upload(
                filename,
                file_bytes,
                {
                    "content-type": file.content_type,
                    "upsert": "false"
                }
            )

            image_url = supabase.storage.from_("post-images").get_public_url(filename)

        post = Post(
            user_id=session["user_id"],
            content=content,
            image=image_url
        )

        db.session.add(post)
        db.session.commit()

        return redirect("/community")

    return render_template("create_post.html")
@app.route("/add-comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):

    if "user_id" not in session:
        return redirect("/login")

    content = request.form["content"]

    comment = Comment(
        post_id=post_id,
        user_id=session["user_id"],
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return redirect("/community")

@app.route("/delete-post/<int:post_id>", methods=["POST"])
def delete_post(post_id):

    if "user_id" not in session:
        return redirect("/login")

    post = Post.query.get_or_404(post_id)

    # 🔒 ONLY OWNER CAN DELETE
    if post.user_id != session["user_id"]:
        return "Unauthorized", 403

    db.session.delete(post)
    db.session.commit()

    return redirect("/community")

@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):

    if "user_id" not in session:
        return redirect("/login")

    comment = Comment.query.get_or_404(comment_id)

    # 🔒 ONLY OWNER CAN DELETE COMMENT
    if comment.user_id != session["user_id"]:
        return "Unauthorized", 403

    db.session.delete(comment)
    db.session.commit()

    return redirect("/community")

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):

    if "user_id" not in session:
        return redirect("/login")

    post = Post.query.get_or_404(post_id)

    # ONLY OWNER CAN EDIT
    if post.user_id != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":

        # update text
        post.content = request.form.get("content")

        file = request.files.get("image")

        if file and file.filename:

            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file_bytes = file.read()

            # upload new image
            supabase.storage.from_("post-images").upload(
                filename,
                file_bytes,
                {
                    "content-type": file.content_type,
                    "upsert": "false"
                }
            )

            new_url = supabase.storage.from_("post-images").get_public_url(filename)

            # delete old image (optional but good)
            if post.image:
                try:
                    old_file = post.image.split("/")[-1]
                    supabase.storage.from_("post-images").remove([old_file])
                except:
                    pass

            post.image = new_url

        db.session.commit()

        return redirect("/community")

    return render_template("edit_post.html", post=post)


@app.route("/like-post/<int:post_id>", methods=["POST"])
def like_post(post_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    # 👉 If already liked → remove like (unlike)
    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)

    db.session.commit()

    return redirect("/community")
# ▶️ RUN APP
if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
