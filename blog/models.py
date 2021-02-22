from datetime import datetime
from blog import login
from blog import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Posts", backref='author', lazy='dynamic', cascade="all,delete")
    comments = db.relationship("Comments", backref="author", lazy="dynamic", cascade="all,delete")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64))
    content = db.Column(db.String(2000))
    publication_datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship("Comments", backref="post", lazy="dynamic", cascade="all,delete")

    def __repr__(self):
        return f"<Post {self.title}>"


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64))
    content = db.Column(db.String(1000))
    publication_datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment {self.title}>"

