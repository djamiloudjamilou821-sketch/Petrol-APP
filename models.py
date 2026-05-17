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

    formula = db.Column(db.String(200), nullable=False)

    desc = db.Column(db.String(500))

    link = db.Column(db.String(200))