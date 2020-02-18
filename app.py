import flask
import time
from flask import render_template, redirect, url_for, request
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import testing_development

app = flask.Flask(__name__)

@app.route('/testd')
def testd():
    def inner():
        for x in dir(testing_development):
            item = getattr(testing_development, x)
            print(item)
            if callable(item):
                if not item.__name__ in ['assert_result', 'Service']:
                    time.sleep(1)
                    yield '%s<br/>\n' % item()

    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('result.html')
    return flask.Response(tmpl.generate(result=inner()))

@app.route('/')
def index():

    return render_template('index.html')

app.run(debug=True, host='0.0.0.0', port='5001')
