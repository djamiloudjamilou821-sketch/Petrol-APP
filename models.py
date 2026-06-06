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

    posts = db.relationship(
        "Post",
        backref=db.backref("user", passive_deletes=True),
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "Like",
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    # PROFILE
    bio = db.Column(db.Text)

    profile_pic = db.Column(db.String(300))

    country = db.Column(db.String(100))

    university = db.Column(db.String(200))

    petroleum_level = db.Column(db.String(100))

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    image = db.Column(db.String(300))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    comments = db.relationship(
        "Comment",
        backref="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    likes = db.relationship(
        "Like",
        backref="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
class Comment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user = db.relationship("User", backref="comments")

class Like(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())