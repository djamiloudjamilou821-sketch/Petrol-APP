from database import db

# =========================
# LESSON MODEL
# =========================

class Lesson(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    video = db.Column(db.String(500), nullable=False)

    content = db.Column(db.Text, nullable=False)


# =========================
# FORMULA MODEL
# =========================

class Formula(db.Model):


    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    equation = db.Column(db.Text)

    description = db.Column(db.Text)

    variables = db.Column(db.Text)

    example = db.Column(db.Text)

    category = db.Column(db.String(100))

    python_formula = db.Column(db.Text)
