from flask import render_template, request, redirect, session

# SIMPLE ADMIN PASSWORD (you can change it anytime)
ADMIN_PASSWORD = "1234"  # 🔐 change this later

def register_auth(app):

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


    @app.route("/logout")
    def logout():
        session.pop("admin", None)
        return redirect("/admin-login")