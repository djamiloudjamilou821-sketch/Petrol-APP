from flask import render_template, request, redirect, session
from models import Lesson, Formula
from database import db

def admin_required():
    if not session.get("admin"):
        return redirect("/admin-login")
    return None

# =========================================
# REGISTER ADMIN ROUTES
# =========================================

def register_admin(app):


    # =====================================
    # EDIT LESSON
    # =====================================

    @app.route("/admin/edit-lesson/<int:id>", methods=["GET", "POST"])
    def edit_lesson(id):
        if not session.get("admin"):
            return redirect("/admin-login")

        lesson = Lesson.query.get_or_404(id)
        
        if request.method == "POST":

            lesson.title = request.form["title"]
            lesson.video = request.form["video"]
            lesson.content = request.form["content"]

            db.session.commit()

            return redirect("/admin")

        return render_template(
            "admin/edit_lesson.html",
            lesson=lesson,
            id=id
        )
    # =====================================
    # ADMIN HOME
    # =====================================

    @app.route("/admin")
    def admin_home():

        if not session.get("admin"):
            return redirect("/admin-login")

        lessons = Lesson.query.all()
        formulas = Formula.query.all()

        return render_template(
            "admin/home.html",
            lessons=lessons,
            formulas=formulas
        )

    # LOGOUT
    @app.route("/admin-logout")
    def admin_logout():
        session.pop("admin", None)
        return redirect("/admin-login")

    # =====================================
    # ADD LESSON
    # =====================================

    @app.route("/admin/add-lesson", methods=["GET", "POST"])
    def add_lesson():

        if not session.get("admin"):
            return redirect("/admin-login")

        if request.method == "POST":

            lesson = Lesson(
                title=request.form["title"],
                video=request.form["video"],
                content=request.form["content"]
            )

            db.session.add(lesson)
            db.session.commit()

            return redirect("/admin")

        return render_template("admin/add_lesson.html")

    # =====================================
    # ADD FORMULA
    # =====================================

    @app.route("/admin/add-formula", methods=["GET", "POST"])
    def add_formula():

        if not session.get("admin"):
            return redirect("/admin-login")

        if request.method == "POST":

            formula = Formula(
                name=request.form["name"],
                equation=request.form["equation"],
                description=request.form["description"],
                variables=request.form["variables"],
                python_formula=request.form["python_formula"],
                category=request.form["category"]
            )

            db.session.add(formula)
            db.session.commit()

            return redirect("/formulas")

        return render_template("admin/add_formula.html")
    # MANAGE LESSONS
    @app.route("/admin/manage-lessons")
    def manage_lessons():
        if not session.get("admin"):
            return redirect("/admin-login")

        lessons = Lesson.query.all()

        return render_template(
            "admin/manage_lessons.html",
            lessons=lessons
        )

    # DELETE
    @app.route("/admin/delete-lesson/<int:id>")
    def delete_lesson(id):

        if not session.get("admin"):
            return redirect("/admin-login")

        lesson = Lesson.query.get_or_404(id)

        db.session.delete(lesson)
        db.session.commit()

        return redirect("/admin/manage-lessons")

    # EDIT FORMULA
    @app.route("/admin/edit-formula/<int:id>", methods=["GET", "POST"])
    def edit_formula(id):

        if not session.get("admin"):
            return redirect("/admin-login")

        formula = Formula.query.get_or_404(id)

        if request.method == "POST":

            formula.name = request.form["name"]

            formula.equation = request.form["equation"]

            formula.description = request.form["description"]

            formula.variables = request.form["variables"]

            formula.category = request.form["category"]

            formula.python_formula = request.form["python_formula"]

            db.session.commit()

            return redirect("/admin/manage-formulas")

        return render_template("admin/edit_formula.html", formula=formula)

    # DELETE FORMULA
    @app.route("/admin/delete-formula/<int:id>")
    def delete_formula(id):

        if not session.get("admin"):
            return redirect("/admin-login")

        formula = Formula.query.get_or_404(id)

        db.session.delete(formula)
        db.session.commit()

        return redirect("/admin/manage-formulas")

    # MANAGE FORMULA
    @app.route("/admin/manage-formulas")
    def manage_formulas():

        if not session.get("admin"):
            return redirect("/admin-login")

        formulas = Formula.query.all()

        return render_template("admin/manage_formulas.html", formulas=formulas)
        return render_template("admin/manage_formulas.html", formulas=formulas)
