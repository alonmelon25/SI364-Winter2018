# An application about recording favorite songs & info

# 1:Many relationship: Album:Song(s)
# Many:Many relationship: Artists:Songs
# TODO: E-R diagram to display
# TODO: relationship to build (done, ish)
# TODO: relationship and association table to build

import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
# from flask_sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Date, Time
# from flask_sqlalchemy import relationship, backref

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/songs_db_2"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug stuff
manager = Manager(app)
# moment = Moment(app) # For time # Later
db = SQLAlchemy(app) # For database use

#########
######### Everything above this line is important/useful setup, not problem-solving.
#########

##### Set up Models #####

# Set up association Table between artists and albums
collections = db.Table('collections',db.Column('album_id',db.Integer, db.ForeignKey('albums.id')),db.Column('artist_id',db.Integer, db.ForeignKey('artists.id')))
playlists_collections = db.Table('playlists_collections',db.Column('song_id',db.Integer, db.ForeignKey('songs.id')),db.Column('playlist_id',db.Integer, db.ForeignKey('playlists.id')))

class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    artists = db.relationship('Artist',secondary=collections,backref=db.backref('albums',lazy='dynamic'),lazy='dynamic')
    songs = db.relationship('Song',backref='Album')


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    songs = db.relationship('Song',backref='Artist')

    def __repr__(self):
        return "{} (ID: {})".format(self.name,self.id)

class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),unique=True) # Only unique title songs
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    genre = db.Column(db.String(64))

    def __repr__(self):
        return "{} | {}".format(self.title,self.genre)

class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),unique=True)
    songs = db.relationship('Song',secondary=playlists_collections,backref=db.backref('playlists',lazy='dynamic'),lazy='dynamic')


##### Set up Forms #####

class SongForm(FlaskForm):
    song = StringField("What is the title of your favorite song?", validators=[Required()])
    artist = StringField("What is the name of the artist who performs it?",validators=[Required()])
    genre = StringField("What is the genre of that song?", validators
        =[Required()])
    album = StringField("What is the album this song is on?", validators
        =[Required()])
    submit = SubmitField('Submit')

class PlaylistForm(FlaskForm):
    name = StringField("What is the title of the playlist?", validators=[Required()])
    # Only creating a multiple select field, haven't initialized it yet!
    songs = SelectMultipleField("Select the songs you want to add to this playlist")
    submit = SubmitField('Submit')

##### Helper functions

### For database additions / get_or_create functions

def get_or_create_artist(db_session,artist_name):
    artist = db_session.query(Artist).filter_by(name=artist_name).first()
    if artist:
        return artist
    else:
        artist = Artist(name=artist_name)
        db_session.add(artist)
        db_session.commit()
        return artist

def get_or_create_album(db_session, album_name, artists_list=[]):
    album = db_session.query(Album).filter_by(name=album_name).first() # by name filtering for album
    if album:
        return album
    else:
        album = Album(name=album_name)
        for artist in artists_list:
            artist = get_or_create_artist(db_session,artist)
            album.artists.append(artist)
        db_session.add(album)
        db_session.commit()
    return album

def get_or_create_song(db_session, song_title, song_artist, song_album, song_genre):
    song = db_session.query(Song).filter_by(title=song_title).first()
    if song:
        print('Found song')
        return song
    else:
        artist = get_or_create_artist(db_session, song_artist)
        album = get_or_create_album(db_session, song_album, artists_list=[song_artist]) # list of one song artist each time -- check out get_or_create_album and get_or_create_artist!
        song = Song(title=song_title,genre=song_genre,artist_id=artist.id,album_id=album.id)
        db_session.add(song)
        db_session.commit()
        return song

def get_or_create_playlist(db_session, playlist_title, selected_songs):
    playlist = db_session.query(Playlist).filter_by(title=playlist_title).first()
    if playlist:
        return playlist
    else:
        playlist = Playlist(title=playlist_title)
        for song_title in selected_songs:
            ## Don't have song artist, album and genre information. So passing those as empty parameters
            s = get_or_create_song(db_session,song_title,'','','')
            ## Appending each returned song to the relationship property of playlist object
            playlist.songs.append(s)
        db_session.add(playlist)
        db_session.commit()
        return playlist



##### Set up Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Main route

@app.route('/', methods=['GET', 'POST'])
def index():
    songs = Song.query.all()
    num_songs = len(songs)
    form = SongForm()
    if form.validate_on_submit():
        if db.session.query(Song).filter_by(title=form.song.data).first(): # If there's already a song with that title, though...nvm. Gotta add something like "(covered by..)"
            flash("You've already saved a song with that title!")
        get_or_create_song(db.session,form.song.data, form.artist.data, form.album.data, form.genre.data)
        return redirect(url_for('see_all'))
    return render_template('index.html', form=form,num_songs=num_songs)

@app.route('/all_songs')
def see_all():
    all_songs = [] # To be tuple list of title, genre
    songs = Song.query.all()
    for s in songs:
        artist = Artist.query.filter_by(id=s.artist_id).first()
        all_songs.append((s.title,artist.name, s.genre))
    return render_template('all_songs.html',all_songs=all_songs)

@app.route('/all_artists')
def see_all_artists():
    artists = Artist.query.all()
    names = [(a.name, len(Song.query.filter_by(artist_id=a.id).all())) for a in artists]
    return render_template('all_artists.html',artist_names=names)

@app.route('/playlists', methods=['GET', 'POST'])
def create_playlists():
    form = PlaylistForm()
    songs = Song.query.all()
    song_titles = [(s.title,s.title) for s in songs]
    ## Initilizing the multiple select filed of playlist form dynamically with all the songs in the database
    form.songs.choices = song_titles
    if form.validate_on_submit():
        playlist_name = form.name.data
        songs_selected = form.songs.data
        print(songs_selected)
        get_or_create_playlist(db.session,playlist_name,songs_selected)
        return redirect(url_for('see_all_playlists'))
    return render_template('playlist_form.html',form=form)

@app.route('/all_playlists')
def see_all_playlists():
    playlists = Playlist.query.all()
    playlist_names = []
    for p in playlists:
        ## Querying the association table and filtering using playlist ID to count number of songs in any given playlist.
        total_songs = db.session.query(playlists_collections).filter_by(playlist_id=p.id).all()
        playlist_names.append((p.title,len(total_songs)))
    # reusing artist_names template
    return render_template('all_artists.html',artist_names=playlist_names)

if __name__ == '__main__':
    db.create_all()
    manager.run() # NEW: run with this: python main_app.py runserver
    # Also provides more tools for debugging
