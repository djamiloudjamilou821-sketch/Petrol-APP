from flask import Flask, jsonify, request, session, redirect, render_template, url_for
from database import db
from models import Lesson, Formula, User, Post, Comment, Like
from datetime import timedelta
from werkzeug.utils import secure_filename

import requests
from dotenv import load_dotenv
load_dotenv()

from lessons import register_lessons
from quiz import register_quiz
from formulas import register_formulas
from converter import register_converter
from admin import register_admin
from auth import register_auth
import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="deo1uyu3z",   # ← replace this
    api_key="795759859987232",         # ← replace this
    api_secret="PDpz-mXnbGfPWVZH4e7aU-hP0gY",   # ← replace this
    secure=True
)

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


# Helper function to check if request is looking for a JSON response
def prefers_json():
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest" or
        "application/json" in request.headers.get("Accept", "") or
        request.is_json
    )


# 🏠 HOME PAGE (Now the default entry point of your app)
@app.route("/")
@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect("/login")

    # We hardcode "en" here so your templates don't break if they still look for the 'lang' variable
    return render_template("index.html", lang="en")

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


@app.route("/petroai")
def petroai_page():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("petroai.html")

@app.route("/ask_petroai", methods=["POST"])
def ask_petroai():
    if "user_id" not in session:
        return jsonify({"answer": "Please log in to talk with PetroAI."}), 401

    # 🔍 DATABASE LOOKUP: Fetch the real name using the user_id
    current_user = User.query.get(session["user_id"])
    
    # Safely get the username from the DB model, fallback to 'Student' if not found
    if current_user and hasattr(current_user, 'username'):
        user_name = current_user.username
    elif current_user and hasattr(current_user, 'name'):
        user_name = current_user.name
    else:
        user_name = "Student"

    question = request.json.get("question")

    # 🧠 INIT MEMORY
    if "chat_history" not in session:
        session["chat_history"] = []

    # ADD USER MESSAGE TO MEMORY
    session["chat_history"].append({
        "role": "user",
        "content": question
    })

    # Keep last 10 messages only
    session["chat_history"] = session["chat_history"][-10:]

    # SYSTEM MESSAGE (Now injects the dynamic, real database name!)
    system_message = {
        "role": "system",
        "content": (
            "You are PetroAI, the official assistant of PetroApp, a petroleum engineering learning platform."
            "About PetroApp:"
            "- It teaches petroleum engineering through lessons, quizzes, and calculators, and community where users share knwoledge"
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
             f"The current user is called {user_name}."  # <-- Dynamic Name Check!
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

    # BUILD MESSAGES
    messages = [system_message] + session["chat_history"]

    # API REQUEST
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

    # SAVE ASSISTANT RESPONSE
    session["chat_history"].append({
        "role": "assistant",
        "content": answer
    })

    session.modified = True
    return jsonify({"answer": answer})

# COMMUNITY
from datetime import datetime

@app.route("/community")
def community():
    if "user_id" not in session:
        return redirect("/login")

    # 1. Check if the user exists in the DB
    current_user = User.query.get(session["user_id"])
    if not current_user:
        session.clear()
        return redirect("/login")

    # 2. Get the list of posts to display on the page
    posts = Post.query.order_by(Post.created_at.desc()).all()

    # 3. Mark this exact moment as their "last visit timestamp"
    # We save it as an ISO string so the session cookie can store it easily
    session["last_community_visit"] = datetime.utcnow().isoformat()
    session.modified = True

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

    # DB Protection verification guard
    current_user = User.query.get(session["user_id"])
    if not current_user:
        session.clear()
        return redirect("/login")

    if request.method == "POST":
        content = request.form.get("content")
        file = request.files.get("image")
        image_url = None

        if file and file.filename != "":
            upload_result = cloudinary.uploader.upload(
                file,
                folder="petroapp_posts"
            )
            image_url = upload_result.get("secure_url")

        post = Post(
            user_id=session["user_id"],
            content=content,
            image=image_url
        )

        db.session.add(post)
        db.session.commit()

        return redirect("/community")

    return render_template("create_post.html")

# UPDATED ASYNC COMMENT CREATION (FIXED INTERCEPT ENGINE)
@app.route("/add-comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if "user_id" not in session:
        if prefers_json():
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect("/login")

    # Verify session active in DB map context
    current_user = User.query.get(session["user_id"])
    if not current_user:
        session.clear()
        if prefers_json():
            return jsonify({"success": False, "error": "User does not exist"}), 401
        return redirect("/login")

    # Accept both standard forms and incoming JSON payload configurations
    if request.is_json:
        content = request.json.get("content")
    else:
        content = request.form.get("content")

    comment = Comment(
        post_id=post_id,
        user_id=session["user_id"],
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    if prefers_json():
        post = Post.query.get(post_id)
        return jsonify({
            "success": True,
            "comment_id": comment.id,
            "content": comment.content,
            "username": current_user.username if hasattr(current_user, 'username') else session.get("user_name", "Student"),
            "user_id": session["user_id"],
            "comment_count": len(post.comments) if post else 0
        })

    return redirect("/community")

@app.route("/delete-post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user_id" not in session:
        return redirect("/login")

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        return "Unauthorized", 403

    if post.image:
        try:
            import re
            public_id = post.image.split("/")[-1].split(".")[0]
            cloudinary.uploader.destroy(f"petroapp_posts/{public_id}")
        except:
            pass

    db.session.delete(post)
    db.session.commit()

    return redirect("/community")

# UPDATED ASYNC COMMENT DELETION (FIXED INTERCEPT ENGINE)
@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    if "user_id" not in session:
        if prefers_json():
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect("/login")

    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id

    if comment.user_id != session["user_id"]:
        if prefers_json():
            return jsonify({"success": False, "error": "Forbidden"}), 403
        return "Unauthorized", 403

    db.session.delete(comment)
    db.session.commit()

    if prefers_json():
        post = Post.query.get(post_id)
        return jsonify({
            "success": True,
            "comment_count": len(post.comments) if post else 0
        })

    return redirect("/community")

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "user_id" not in session:
        return redirect("/login")

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":
        post.content = request.form.get("content")
        file = request.files.get("image")

        if file and file.filename != "":
            upload_result = cloudinary.uploader.upload(
                file,
                folder="petroapp_posts"
            )
            post.image = upload_result.get("secure_url")

        db.session.commit()
        return redirect("/community")

    return render_template("edit_post.html", post=post)

# UPDATED ASYNC LIKE ENGINE (FIXED INTERCEPT ENGINE)
@app.route("/like-post/<int:post_id>", methods=["POST"])
def like_post(post_id):
    if "user_id" not in session:
        if prefers_json():
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect("/login")

    # DB Protection verification guard
    current_user = User.query.get(session["user_id"])
    if not current_user:
        session.clear()
        if prefers_json():
            return jsonify({"success": False, "error": "User does not exist"}), 401
        return redirect("/login")

    user_id = session["user_id"]
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    status = ""

    if like:
        db.session.delete(like)
        status = "unliked"
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        status = "liked"

    db.session.commit()

    if prefers_json():
        post = Post.query.get(post_id)
        return jsonify({
            "success": True,
            "status": status,
            "like_count": len(post.likes) if post else 0
        })

    return redirect("/community")

from datetime import datetime

@app.context_processor
def inject_new_posts_count():
    # If the user isn't logged in, there are 0 new posts
    if "user_id" not in session:
        return dict(new_posts_count=0)
        
    last_visit_str = session.get("last_community_visit")
    
    # If they have NEVER visited the community page before, count all posts from the last 24 hours as new
    if not last_visit_str:
        # Change this to Post.query.count() if you want to count every post in the DB instead
        new_count = Post.query.count() 
        return dict(new_posts_count=new_count)
        
    # Convert the saved string timestamp back into a Python datetime object
    last_visit = datetime.fromisoformat(last_visit_str)
    
    # Query the database: Count how many posts have a created_at time greater than our last visit
    new_count = Post.query.filter(Post.created_at > last_visit).count()
    
    return dict(new_posts_count=new_count)
# ▶️ RUN APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)