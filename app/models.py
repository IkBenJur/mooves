from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=mp&s={size}"

    def __repr__(self):
        return f"{self.username}"
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(64), index=True, unique=True)
    movies = db.Relationship("Movie", backref="genre", lazy="dynamic")

    def __repr__(self):
        return f"{self.genre}"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    #db.ForeignKey gebruikt de SQLAlchemy table name dus lowercase (snakecase voor multi word)
    #db.Relationship gebruikt de modelclass naam
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))

    def __repr__(self):
        return f"{self.title}"