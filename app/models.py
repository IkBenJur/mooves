from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

user_movie = db.Table("user_movie",
                      db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                      db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"))
                )

movie_genre = db.Table('movie_genre',
                       db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
                       db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
                       )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship("Review", backref="author", lazy="dynamic")
    favourites = db.relationship("Movie", secondary=user_movie,
                                backref=db.backref("favourited", lazy="dynamic"), lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=mp&s={size}"
    
    def favourite(self, movie):
        if not self.is_favourited(movie):
            self.favourites.append(movie)

    def unfavourite(self, movie):
        if self.is_favourited(movie):
            self.favourites.remove(movie)

    def is_favourited(self, movie):
        return self.favourites.filter(
            user_movie.c.movie_id == movie.id
        ).count() > 0

    def __repr__(self):
        return f"{self.username}"
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #db.ForeignKey gebruikt de SQLAlchemy table name dus lowercase (snakecase voor multi word)
    #db.Relationship gebruikt de modelclass naam
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))
    reviewBody = db.Column(db.String(140))
    stars = db.Column(db.Integer, index=True)

    def recent_Reviews():
        return Review.query.order_by(Review.id.desc()).limit(5).all()

    def __repr__(self):
        return f"{self.reviewBody}"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    reviews = db.relationship("Review", backref="subject", lazy="dynamic")
    genres = db.relationship('Genre', secondary=movie_genre, lazy="dynamic",
                              backref=db.backref('movies', lazy="dynamic"))
    #db.ForeignKey gebruikt de SQLAlchemy table name dus lowercase (snakecase voor multi word)
    #db.Relationship gebruikt de modelclass naam
    # genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))

    def __repr__(self):
        return f"{self.title}"
    
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.name}"
