from app import app, db
from app.models import User, Genre, Movie

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Genre": Genre, "Movie": Movie}