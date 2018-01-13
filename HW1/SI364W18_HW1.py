## HW 1
## SI 364 W18
## 1000 points

#################################
## Name: Aaron Cheng
## List below here, in a comment/comments, the people you worked with on this assignment AND any resources you used to find code (50 point deduction for not doing so). If none, write "None".

import json
import requests
from datetime import datetime as dt

## [PROBLEM 1] - 150 points
## Below is code for one of the simplest possible Flask applications. Edit the code so that once you run this application locally and go to the URL 'http://localhost:5000/class', you see a page that says "Welcome to SI 364!"

from flask import Flask, request
app = Flask(__name__)
app.debug = True

@app.route('/')
def hello_to_you():
    return 'Hello!'

@app.route('/class')
def welcome_statement():
    return 'Welcome to SI 364!'


## [PROBLEM 2] - 250 points
## Edit the code chunk above again so that if you go to the URL 'http://localhost:5000/movie/<name-of-movie-here-one-word>' you see a big dictionary of data on the page. For example, if you go to the URL 'http://localhost:5000/movie/ratatouille', you should see something like the data shown in the included file sample_ratatouille_data.txt, which contains data about the animated movie Ratatouille. However, if you go to the url http://localhost:5000/movie/titanic, you should get different data, and if you go to the url 'http://localhost:5000/movie/dsagdsgskfsl' for example, you should see data on the page that looks like this:

# {
#  "resultCount":0,
#  "results": []
# }


## You should use the iTunes Search API to get that data.
## Docs for that API are here: https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/
## Of course, you'll also need the requests library and knowledge of how to make a request to a REST API for data.

## Run the app locally (repeatedly) and try these URLs out!

@app.route('/movie/<name>')
def movie_name(name):
    url = "https://itunes.apple.com/search"
    params = {"media": "movie", "term": name}
    get_name = requests.get(url, params = params)
    json_format = json.loads(get_name.text)
    return get_name.text


## [PROBLEM 3] - 250 points

## Edit the above Flask application code so that if you run the application locally and got to the URL http://localhost:5000/question, you see a form that asks you to enter your favorite number.
## Once you enter a number and submit it to the form, you should then see a web page that says "Double your favorite number is <number>". For example, if you enter 2 into the form, you should then see a page that says "Double your favorite number is 4". Careful about types in your Python code!
## You can assume a user will always enter a number only.

@app.route('/question', methods= ['POST', 'GET'])
def fav_num():
    i= """<!DOCTYPE html>
<html>
<body>
<form action="/result" method="GET">
<div>
    Enter favorite number:
    <input type= "text" name= "number" value= "0">
    <br> <br>
    <input type= "submit" value= "Submit"
</div>
</form>
</body>
</html>"""

    return i

@app.route('/result', methods= ['POST', 'GET'])
def doubled_num():
    if request.method == 'GET':
        double = request.args
        favorite = double.get('number')
        multiply = 2 * (int(favorite))
        return "Double your favorite number is {}".format(multiply)

## [PROBLEM 4] - 350 points

## Come up with your own interactive data exchange that you want to see happen dynamically in the Flask application, and build it into the above code for a Flask application, following a few requirements.

## You should create a form that appears at the route: http://localhost:5000/problem4form

## Submitting the form should result in your seeing the results of the form on the same page.

## What you do for this problem should:
# - not be an exact repeat of something you did in class
# - must include an HTML form with checkboxes and text entry
# - should, on submission of data to the HTML form, show new data that depends upon the data entered into the submission form and is readable by humans (more readable than e.g. the data you got in Problem 2 of this HW). The new data should be gathered via API request or BeautifulSoup.

# You should feel free to be creative and do something fun for you --
# And use this opportunity to make sure you understand these steps: if you think going slowly and carefully writing out steps for a simpler data transaction, like Problem 1, will help build your understanding, you should definitely try that!

# You can assume that a user will give you the type of input/response you expect in your form; you do not need to handle errors or user confusion. (e.g. if your form asks for a name, you can assume a user will type a reasonable name; if your form asks for a number, you can assume a user will type a reasonable number; if your form asks the user to select a checkbox, you can assume they will do that.)

# Points will be assigned for each specification in the problem.
@app.route('/problem4form', methods= ['POST', 'GET'])
def time_selection():
    i= """<!DOCTYPE html>
<html>
<body>
<form action="/problem4result" method="GET">
<div>
    Select a timeframe to retrive weather information from Ann Arbor: <br>
    <input type= "radio" name= "options" value= "Hour"> Hour <br>
    <input type= "radio" name= "options" value= "Day"> Day <br>
    <br>
    <input type= "submit" value= "Next"
</div>
</form>
</body>
</html>"""

    return i

@app.route('/problem4result', methods= ['POST', 'GET'])
def get_weather_data():
    if request.method == 'GET':
        result = request.args
        chosen_time = result.get('options')

        if chosen_time == "Hour":
            base_url = 'https://api.darksky.net/forecast/'
            api_key = 'fc81cbec4d2940e71ab13cf15e4d50ef'
            latitude = str(42.280841)
            longitude = str(-83.738115)
            full_url = base_url + api_key + '/' + latitude + ',' + longitude
            response = requests.get(full_url)
            data = json.loads(response.text)
            hourly = data['hourly']['data']
            for day in hourly:
                time = dt.fromtimestamp(day['time'])
                summary = day['summary']
                temp = day['temperature']
                humid = day['humidity']
                return "Time: {}".format(time) + "<br>" + "Summary: {}".format(summary) + "<br>" + "Temperature: {:10}".format(temp) + "<br>" + "Humidity: {}".format(humid)
        elif chosen_time == "Day":
            base_url = 'https://api.darksky.net/forecast/'
            api_key = 'fc81cbec4d2940e71ab13cf15e4d50ef'
            latitude = str(42.280841)
            longitude = str(-83.738115)
            full_url = base_url + api_key + '/' + latitude + ',' + longitude
            response = requests.get(full_url)
            data = json.loads(response.text)
            daily = data['daily']['data']
            for day in daily:
                time = dt.fromtimestamp(day['time'])
                summary = day['summary']
                high_temp = day['temperatureHigh']
                low_temp = day['temperatureLow']
                return "Time: {}".format(time) + "<br>" + "Summary: {}".format(summary) + "<br>" + "Highest Temperature: {}".format(high_temp) + "<br>" + "Lowest Temperature: {}".format(low_temp)


if __name__ == '__main__':
    app.run()
