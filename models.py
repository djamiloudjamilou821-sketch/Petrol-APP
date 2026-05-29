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

# users

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    country = db.Column(
        db.String(100)
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    # PROFILE
    bio = db.Column(db.Text)

    profile_pic = db.Column(db.String(300))

    country = db.Column(db.String(100))

    university = db.Column(db.String(200))

    petroleum_level = db.Column(db.String(100))