###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell # For debugging purposes
import json
import requests

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/proaaron364Midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
manager = Manager(app) # In order to use manager
db = SQLAlchemy(app) # For database use

###################
#### API Setup ####
###################

def get_movie_info(title):
    url = 'http://www.omdbapi.com/?apikey=9d267298&'
    img = 'http://img.omdbapi.com/?apikey=9d267298&'
    params = {'t': title}
    r = requests.get(url, params = params).json()
    return r

######################################
######## HELPER FXNS (If any) ########
######################################




##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    year = db.Column(db.String(4))
    rated = db.Column(db.String(16))
    released = db.Column(db.String(16))
    runtime = db.Column(db.String(16))
    genre = db.Column(db.String(64))
    director = db.Column(db.String(256))
    moods = db.relationship('Mood', backref='Movie')

class Mood(db.Model):
    __tablename__ = "moods"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    mood = db.Column(db.String(16))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id')) # One-to-many relationship --> One mood, many movies

###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.", validators=[Required()])
    submit = SubmitField()

class MovieForm(FlaskForm):
    title = StringField("Enter name of movie:", validators= [Required(), Length(1,128)])
    submit = SubmitField()

class MoodForm(FlaskForm):
    title = StringField("Enter name of movie:", validators=[Required(), Length(1,128)])
    mood_selection = RadioField("Select mood for movie", choices= [('Educated', 'Educated'),
    ('Humored', 'Humored'), ('Inspired', 'Inspired'), ('Romanced', 'Romanced'),
    ('Scared', 'Scared'), ('Thrilled', 'Thrilled')], validators= [Required()])
    submit = SubmitField()

#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name=name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/all_names')
def all_names():
    names = Name.query.all()
    all_names = []
    for n in names:
        tup = (n.name)
        all_names.append(tup)
    return render_template('name_example.html', all_names=all_names)

@app.route('/movie', methods= ['GET','POST'])
def movie():
    form = MovieForm()

    if form.validate_on_submit():
        title = form.title.data
        movie = Movie.query.filter_by(title=title).first()
        if movie == None:
            movie_info = get_movie_info(title)
            title = movie_info['Title']
            year = movie_info['Year']
            rated = movie_info['Rated']
            released = movie_info['Released']
            runtime = movie_info['Runtime']
            genre = movie_info['Genre']
            director = movie_info['Director']
            # Create object
            movie_entry = Movie(title=title, year=year, rated=rated,
            released=released, runtime=runtime, genre=genre, director=director)
            # Save entry
            db.session.add(movie_entry)
            # Commit
            db.session.commit()
        else:
            title = movie.title
            year = movie.year
            rated = movie.rated
            released = movie.released
            runtime = movie.runtime
            genre = movie.genre
            director = movie.director
        return render_template('movie_info.html', title=title, year=year, rated=rated,
        released=released, runtime=runtime, genre=genre, director=director)
    return render_template('search_movie.html', form=form)

@app.route('/all_movies')
def all_movies():
    movies = Movie.query.all()
    return render_template('all_movies.html', movies= movies)

@app.route('/mood_entry')
def mood_entry():
    form = MoodForm()
    return render_template('mood_entry.html', form=form)

@app.route('/mood', methods= ['GET','POST'])
def mood():
    form = MoodForm(request.form)

    if form.validate_on_submit():
        title = form.title.data
        mood_selection = form.mood_selection.data
        mood = Mood.query.filter_by(title=title, mood=mood_selection).first()
        movie = Movie.query.filter_by(title=title).first()
        if not movie:
            movie_info = get_movie_info(title)
            title = movie_info['Title']
            year = movie_info['Year']
            rated = movie_info['Rated']
            released = movie_info['Released']
            runtime = movie_info['Runtime']
            genre = movie_info['Genre']
            director = movie_info['Director']
            # Create object
            movie = Movie(title=title, year=year, rated=rated,
            released=released, runtime=runtime, genre=genre, director=director)
            # Save entry
            db.session.add(movie_entry)
            # Commit
            db.session.commit()
        if not mood:
            mood = Mood(title=title, mood=mood_selection, movie_id=movie.id)
            db.session.add(mood)
            db.session.commit()
        flash("Entry successfully added!")
        return render_template('mood_info.html', title=mood.title, mood=mood.mood, movie_id=mood.id)
    return render_template('base.html', form=form)

@app.route('/all_moods')
def all_moods():
    moods = Mood.query.all()
    all_moods = []
    for m in moods:
        tup = (m.title, m.mood)
        all_moods.append(tup)
    return render_template('all_moods.html', all_moods= all_moods)

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    #app.run(use_reloader=True,debug=True)
    manager.run() # For debugging purposes

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
