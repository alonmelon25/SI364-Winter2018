from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Required

import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.debug = True

class iTunesForm(FlaskForm):
    artist = StringField('Enter artist name:', validators=[Required()])
    results = IntegerField('How many results should the iTunes API return?', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/')
def home():
    return "Hello, world!"

@app.route('/itunes-form')
def form():
    simpleForm = iTunesForm()
    return render_template('itunes-form.html', form=simpleForm)

@app.route('/itunes-result', methods = ['GET', 'POST'])
def result():
    form = iTunesForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        params = {}
        params['term'] = form.artist.data
        params['limit'] = form.results.data
        response = requests.get('https://itunes.apple.com/search', params=params)
        results = json.loads(response.text)['results']
        return render_template('result.html', results = results)
    flash('All fields are required!')
    return redirect(url_for('form'))

if __name__ == '__main__':
    app.run()
