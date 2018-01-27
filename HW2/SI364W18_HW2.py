## SI 364
## Winter 2018
## HW 2 - Part 1
## Name: Aaron Cheng

## This homework has 3 parts, all of which should be completed inside this file (and a little bit inside the /templates directory).

## Add view functions and any other necessary code to this Flask application code below so that the routes described in the README exist and render the templates they are supposed to (all templates provided are inside the templates/ directory, where they should stay).

## As part of the homework, you may also need to add templates (new .html files) to the templates directory.

#############################
##### IMPORT STATEMENTS #####
#############################
from flask import Flask, request, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, ValidationError
from wtforms.validators import Required

import json
import requests

#####################
##### APP SETUP #####
#####################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardtoguessstring'

####################
###### FORMS #######
####################

class AlbumEntryForm(FlaskForm):
    album_name = StringField('Enter the name of an album: ', validators= [Required()])
    album_rating = RadioField("How much do you like this album? (1 low, 3 high)", validators= [Required()], choices= [('1', '1'), ('2', '2'), ('3', '3')])
    submit = SubmitField("Submit")

####################
###### ROUTES ######
####################

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/user/<name>')
def hello_user(name):
    return '<h1>Hello {0}<h1>'.format(name)

@app.route('/artistinfo')
def artistinfo():
    result = request.args
    selected_artist = result.get('artist')
    base_url = "https://itunes.apple.com/search?term="
    url = base_url + selected_artist
    req = requests.get(url).text
    return render_template('artist_info.html', objects = json.loads(req)["results"])

@app.route('/artistlinks')
def artistlinks():
	return render_template("artist_links.html")

@app.route('/artistform')
def artistform():
	return render_template('artistform.html')

@app.route('/specific/song/<artist_name>')
def specific_artist(artist_name):
    base_url = "https://itunes.apple.com/search?term="
    url = base_url + artist_name
    req = requests.get(url).text
    return render_template("specific_artist.html", results= json.loads(req)["results"])

@app.route('/album_entry', methods= ['POST', 'GET'])
def album_entry():
    if request.method == "GET":
        entry_form = AlbumEntryForm()
        return render_template('album_entry.html', form= entry_form)

@app.route('/album_result', methods= ['POST', 'GET'])
def album_result():
    if request.method == "GET":
        name = request.args.get('album_name')
        rating = request.args.get('album_rating')
        results = [name, rating]
        return render_template('album_data.html', results= results)


if __name__ == '__main__':
    app.run(use_reloader=True,debug=True)
