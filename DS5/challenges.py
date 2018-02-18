from flask import Flask, render_template, request
import json
import requests

app = Flask(__name__)

# Challenge 1: Return the 404.html template
# Edit it such that it displays an interesting message

# Challenge 2: Include the link to homepage i.e. http://localhost:5000 in 404.html.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 400

# Challenge 3: Write an error handler for 500 error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Challenge 4: Edit the 500.html template to display link to homepage and link to itunes-form.


@app.route('/')
def index():
    return "Hello, World!"

@app.route('/itunes-form')
def ituneForm():
    return render_template('itunes-form.html')

@app.route('/itunes-result')
def resultTunes():
    if request.method == 'GET':
        result = request.args
        params = {}
        params['term'] = result.get('artist')
        params['limit'] = result.get('num')
        resp = requests.get('https://itunes.apple.com/search?', params = params)
        data = json.loads(resp.text)
        return render_template('list.html', results = data['results'])


if __name__ == '__main__':
    app.run(debug = True)
