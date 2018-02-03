#############################
##### IMPORT STATEMENTS #####
#############################

from flask import Flask, request, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, ValidationError
from wtforms.validators import Required

import json
import requests

###########################
##### APP SETUP #####
###########################

app = Flask(__name__)
app.config['SECRET_KEY'] = '0dbb00ce32032ec820f3d3c00699ee58'
app.debug = True

####################
###### FORMS #######
####################

class WeatherForm(FlaskForm):
    zipcode = StringField('Enter zip code: ', validators= [Required(), Length(5)])
    submit = SubmitField("Submit")

    def validate_zipcode(self, field):
        if len(str(field.data)) != 5:
            raise ValidationError("Please enter a 5 digit zipcode")

####################
###### ROUTES ######
####################

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/zipcode', methods = ["POST", "GET"])
def zipcode():
    form = WeatherForm()

    if form.validate_on_submit():
        zipcode = str(form.zipcode.data)

        params = {}
        params["zip"] = zipcode + ",us"
        params["appid"] = API_KEY
        baseurl = "http://api.openweathermap.org/data/2.5/weather?"
        response = requests.get(baseurl, params = params)
        response_dict = json.loads(response.text)

        description = response_dict["weather"][0]["description"]
        city = response_dict["name"]
        temperature_kelvin = response_dict["main"]["temp"]
        temperature = temperature_kelvin * 1.8 - 459.67 #convert temperature from Kelvin to Fahrenheit

        return render_template('results.html',city=city,description=description,temperature=temperature)

    elif request.method == "GET":
        return render_template('weather_form.html', form=form)

    else:
        flash(form.errors)
        return render_template('weather_form.html', form=form)


if __name__ == "__main__":
    app.run(use_reloader=True,debug=True)
