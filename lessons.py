from flask import render_template, session, redirect
from models import Lesson, LessonProgress
from database import db

def register_lessons(app):
    
    # LESSONS
    @app.route("/lessons")
    def lessons():

        # THE FIX IS HERE: Added .order_by(Lesson.id)
        lessons = Lesson.query.order_by(Lesson.id).all()

        completed_ids = []

        if session.get("user_id"):
            completed_ids = [
                p.lesson_id
                for p in LessonProgress.query.filter_by(
                    user_id=session["user_id"],
                    completed=True
                ).all()
            ]

        return render_template(
            "lessons.html",
            lessons=lessons,
            completed_ids=completed_ids
        )


    @app.route("/lesson/<int:id>")
    def lesson(id):

        lesson = Lesson.query.get_or_404(id)

        completed = False

        user_id = session.get("user_id")

        if user_id:
            completed = LessonProgress.query.filter_by(
                user_id=user_id,
                lesson_id=id
            ).first() is not None

        return render_template(
            "lesson_detail.html",
            lesson=lesson,
            completed=completed
        )

    @app.route("/complete_lesson/<int:lesson_id>")
    def complete_lesson(lesson_id):

        user_id = session.get("user_id")

        if not user_id:
            return redirect("/login")

        existing = LessonProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()

        if not existing:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                completed=True
            )

            db.session.add(progress)
            db.session.commit()

        return redirect(f"/lesson/{lesson_id}")