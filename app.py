import flask
import time
from flask import render_template, redirect, url_for, request
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import testing_queries
from intermine.webservice import Service

app = flask.Flask(__name__)

@app.route('/testd')
def testd():

    service = Service('http://im-dev1.wormbase.org/tools/wormmine/service')

    def inner():
        for x in dir(testing_queries):
            item = getattr(testing_queries, x)
            print(item)
            if callable(item):
                if not item.__name__ in ['assert_result', 'Service', 'assert_greater', 'save_txt_file']:
                    time.sleep(1)
                    yield '%s<br/>\n' % item(service, True)

    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('result.html')
    return flask.Response(tmpl.generate(result=inner()))


@app.route('/testp')
def testp():

    service = Service('http://intermine.wormbase.org/tools/wormmine/service')

    def inner():
        for x in dir(testing_queries):
            item = getattr(testing_queries, x)
            print(item)
            if callable(item):
                if not item.__name__ in ['assert_result', 'Service', 'assert_greater', 'save_txt_file']:
                    time.sleep(1)
                    yield '%s<br/>\n' % item(service)

    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('result.html')
    return flask.Response(tmpl.generate(result=inner()))


@app.route('/')
def index():

    return render_template('index.html')

app.run(debug=True, host='0.0.0.0', port='5001')
