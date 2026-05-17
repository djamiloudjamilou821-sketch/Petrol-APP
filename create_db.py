from app import app
from database import db
from models import Lesson, Formula

with app.app_context():
    db.create_all()

print("Database tables created!")