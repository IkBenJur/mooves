from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, emptyForm, ReviewForm
from app.models import User, Movie, Review, Genre
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import csv

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    movies = Movie.query.all()
    reviews = Review.recent_Reviews()
    form = emptyForm()
    reviewForm = ReviewForm()
    if reviewForm.validate_on_submit():
        # HARD CODED TO ONE MOVIE
        movie = Movie.query.get(3)
        review = Review(subject=movie, reviewBody=reviewForm.review.data,
                        stars=reviewForm.stars.data, author=current_user)
        db.session.add(review)
        db.session.commit()
        flash("You review has been submitted")
        redirect(url_for("index"))
    return render_template("index.html", movies=movies, reviews=reviews, favourite=form, reviewForm=reviewForm)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/user/<username>")
@login_required
def userPage(username):
    u = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(user_id=u.id).all()
    return render_template("userPage.html", user=u, reviews=reviews)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("editProfile.html", form=form)

@app.route("/favourite/<movieTitle>", methods=["POST"])
@login_required
def favourite(movieTitle):
    form = emptyForm()
    if form.validate_on_submit():
        movie = Movie.query.filter_by(title=movieTitle).first()
        if movie is None:
            flash(f"Movie {movieTitle} not found")
            return redirect(url_for("index"))
        current_user.favourite(movie)
        db.session.commit()
        flash(f"You've added a new favourite movie! {movieTitle}")
        return redirect(url_for("userPage", username=current_user.username))
    else:
        return redirect(url_for("index"))
    
@app.route("/unfavourite/<movieTitle>", methods=["POST"])
@login_required
def unfavourite(movieTitle):
    form = emptyForm()
    if form.validate_on_submit():
        movie = Movie.query.filter_by(title=movieTitle).first()
        if movie is None:
            flash(f"Movie {movieTitle} is not found")
            return redirect(url_for("index"))
        current_user.unfavourite(movie)
        db.session.commit()
        flash(f"You unfavourited {movieTitle}")
        return redirect(url_for("userPage", username=current_user.username))
    else:
        return redirect(url_for("index"))
    
@app.route("/movie/<movieId>")
@login_required
def movie(movieId):
    movie = Movie.query.get(movieId)
    if movie is None:
        flash("Movie is not in database")
        #Redirect to previous page
        redirect(url_for())
    return render_template("movie.html", movie=movie)

@app.route("/load_data")
def load_data():
    with open("testingDB\imdb_top_1000.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader((line.rstrip() for line in file), delimiter=',')

        # Read the header and store it in a variable
        header = next(csv_reader)

        # Convert the CSV reader object to a list containing the remaining data
        data_list = [dict(zip(header, row)) for row in csv_reader]


    unique_genres = set()
    for row in data_list:
        genres = row['Genre'].split(',')
        for genre in genres:
            unique_genres.add(genre.strip())

    # Convert the set of unique genres to a list
    unique_genres_list = list(unique_genres)
    # for genre in unique_genres_list:
    #     genre_obj = Genre(name=genre)
    #     db.session.add(genre_obj)
    
    for movie in data_list:
        movie_obj = Movie(title=movie["Series_Title"],
                          year=movie["Released_Year"],
                          rated=movie["Certificate"],
                          runtime=movie["Runtime"],
                          plot=movie["Overview"],
                          metascore=movie["Meta_score"],
                          director=movie["Director"],
                          imdb_rating=movie["IMDB_Rating"],
                          imdb_votes=movie["No_of_Votes"],
                          poster_url=movie["Poster_Link"]
                        )
        # db.session.add(movie_obj)
        for genre in movie["Genre"].split(','):
            genre_obj = Genre.query.filter_by(name=genre.strip()).first()
            if genre_obj != None:
                movie_obj.genres.append(genre_obj)
            
    # db.session.commit()
    return "Data loaded"