import flask
import time

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import testing_development

app = flask.Flask(__name__)

@app.route('/yield')
def index():
    def inner():
        for x in dir(testing_development):
            item = getattr(testing_development, x)
            print(item)
            if callable(item):
                if not item.__name__ in ['assert_result', 'Service']:
                    time.sleep(1)
                    yield '%s<br/>\n' % item()

    # def some_magic():
    #     import a
    #     for i in dir(a):
    #         item = getattr(a, i)
    #         if callable(item):
    #             item()



    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('result.html')
    return flask.Response(tmpl.generate(result=inner()))


app.run(debug=True)
