from flask import render_template
from models import Lesson
def register_lessons(app):
    
    # LESSONS
    @app.route("/lessons")
    def lessons():

        lessons = Lesson.query.all()

        return render_template(
            "lessons.html",
            lessons=lessons
        )


    @app.route("/lesson/<int:id>")
    def lesson(id):

        lesson = Lesson.query.get_or_404(id)

        return render_template(
            "lesson_detail.html",
            lesson=lesson
        )