from flask import Flask, jsonify, request, session, redirect, render_template, url_for
from database import db
from models import Lesson, Formula, User, Post, Comment, Like, Quiz
from datetime import timedelta
from werkzeug.utils import secure_filename
from gemini_quiz import generate_quiz

import requests
from dotenv import load_dotenv
load_dotenv()

from lessons import register_lessons
from formulas import register_formulas
from converter import register_converter
from admin import register_admin
from auth import register_auth
import os
import random
import time
import logging
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=365)

app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.secret_key = os.getenv("SECRET_KEY")
# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# REGISTER ROUTES
register_lessons(app)
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
# Fallback mockup database in case NewsAPI is down or your daily free key tier is exhausted
MOCK_NEWS_FALLBACK = [
    {
        "title": "Advancements in High-Pressure High-Temperature (HPHT) Drilling Fluids",
        "description": "Exploration teams are utilizing optimized synthetic polymer blends to manage deepwater well stability and pressure containment boundaries safely.",
        "source": {"name": "PetroApp Global Ledger"},
        "url": "#",
        "urlToImage": None,
        "publishedAt": "2026-06-10T14:30:00Z"
    },
    {
        "title": "Digital Twin Implementations in Brownfield Reservoir Management",
        "description": "Production operations report an estimated 12% boost in recovery tracking optimization using interconnected downhole sensors and continuous reservoir fluid modeling.",
        "source": {"name": "Energy Engineering Daily"},
        "url": "#",
        "urlToImage": None,
        "publishedAt": "2026-06-09T09:15:00Z"
    }
]

@app.route("/news")
def news():
    # 🔐 SECURE KEY MANAGEMENT: Pull from environment or fallback to your current key string
    api_key = os.environ.get("NEWS_API_KEY", "912b63c6b9554ff5ad722603d2cd8587")
    
    # Target oil, gas, or petroleum industries while explicitly filtering out unrelated junk keywords
    query_string = "(oil OR gas OR petroleum OR reservoir) NOT (cooking OR olive OR vegetable OR gas-prices)"
    
    url = f"https://newsapi.org/v2/everything?q={query_string}&language=en&sortBy=publishedAt&apiKey={api_key}"
    articles = []

    try:
        # Timeout at 5 seconds so your website doesn't hang endlessly if NewsAPI is lagging
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Safely verify that 'articles' is present inside the payload map dictionary
            if "articles" in data:
                raw_articles = data["articles"]
                
                # 🧼 DATA CLEANING FILTER LAYER
                for art in raw_articles:
                    # Drop articles that have been removed or contain empty content fields
                    if art.get("title") == "[Removed]" or not art.get("title"):
                        continue
                        
                    # Calculate an approximate reading timeline metric for the template view
                    word_count = len(art.get("description") or art.get("content") or "")
                    art["read_time"] = max(1, round(word_count / 150))
                    
                    articles.append(art)
            else:
                logging.error(f"NewsAPI error payload structural response: {data}")
                articles = MOCK_NEWS_FALLBACK
        else:
            logging.warning(f"NewsAPI returned status code {response.status_code}. Using backup feed.")
            articles = MOCK_NEWS_FALLBACK

    except Exception as e:
        logging.error(f"Network error trying to fetch news updates: {e}")
        articles = MOCK_NEWS_FALLBACK

    # Slice list down to the best 12 stories so the dashboard doesn't become overly long
    return render_template("news.html", articles=articles[:12])

@app.route("/quiz/<subject>")
def quiz(subject):
    # Initialize a clean session history array identifier unique to this specific subject selection
    session_key = f"history_{subject.lower()}"
    if session_key not in session:
        session[session_key] = []
        
    past_questions = session[session_key]
    
    # 🧠 Run Gemini with history injection tracking
    quiz_data = generate_quiz(subject, history_list=past_questions)
    
    # If the response loaded properly, add the question string text to prevent duplicates later
    if quiz_data.get("error") is None and quiz_data.get("question"):
        past_questions.append(quiz_data["question"])
        session[session_key] = past_questions
        session.modified = True  # Signal Flask to save state changes inside cookies
        
    return render_template(
        "quiz.html",
        subject=subject,
        quiz=quiz_data
    )
@app.route("/quizzes")
def quizzes():
    return render_template("quizzes.html")
# ASK_PETROAI
def call_groq(messages):
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    # Groq serves these incredibly fast (under 1 second)
    models = [
        "llama-3.3-70b-versatile",
        "deepseek-r1-distill-llama-70b"
    ]

    for model in models:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 400  # Slightly lower tokens for faster generation speed
                },
                timeout=3  # ⏱️ Super aggressive timeout. Fast or skip!
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

        except Exception:
            pass

    return None

def call_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    models = [
        "qwen/qwen2.5-72b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free"
    ]

    for model in models:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 400
                },
                timeout=3  # ⏱️ Quick check fallback
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

        except Exception:
            pass

    return None

def call_huggingface(messages):
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json"
    }

    models = [
        "Qwen/Qwen2.5-72B-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct"
    ]

    for model in models:
        try:
            response = requests.post(
                "https://router.huggingface.co/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 400
                },
                timeout=3  # ⏱️ Quick check fallback
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

        except Exception:
            pass

    return None

@app.route("/ask_petroai", methods=["POST"])
def ask_petroai():
    if "user_id" not in session:
        return jsonify({"answer": "Please log in to talk with PetroAI."}), 401

    current_user = User.query.get(session["user_id"])

    if current_user and hasattr(current_user, "username"):
        user_name = current_user.username
    elif current_user and hasattr(current_user, "name"):
        user_name = current_user.name
    else:
        user_name = "Student"

    question = request.json.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please enter a question."})

    if "chat_history" not in session:
        session["chat_history"] = []

    session["chat_history"].append({
        "role": "user",
        "content": question
    })

    session["chat_history"] = session["chat_history"][-10:]

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

    messages = [system_message] + session["chat_history"]
    answer = None

    # ==========================================================
    # 🏎️ 1. GROQ FIRST (Ultra-fast performance lane)
    # ==========================================================
    try:
        answer = call_groq(messages)
        if answer:
            print("✅ Answered instantly by Groq")
    except Exception as e:
        print(f"Groq Route Skipped: {e}")

    # ==========================================================
    # 🥈 2. OPENROUTER BACKUP
    # ==========================================================
    if not answer:
        try:
            answer = call_openrouter(messages)
            if answer:
                print("✅ Answered by OpenRouter Backup")
        except Exception as e:
            print(f"OpenRouter Route Skipped: {e}")

    # ==========================================================
    # 🥉 3. HUGGING FACE BACKUP
    # ==========================================================
    if not answer:
        try:
            answer = call_huggingface(messages)
            if answer:
                print("✅ Answered by Hugging Face Backup")
        except Exception as e:
            print(f"HF Route Skipped: {e}")

    # ==========================================================
    # ALL PROVIDERS TIED UP
    # ==========================================================
    if not answer:
        return jsonify({
            "answer": (
                f"Sorry {user_name}, PetroAI is experiencing heavy traffic "
                "right now. Please try again in a moment."
            )
        })

    session["chat_history"].append({
        "role": "assistant",
        "content": answer
    })

    session["chat_history"] = session["chat_history"][-10:]
    session.modified = True

    return jsonify({"answer": answer})

# ▶️ RUN APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)