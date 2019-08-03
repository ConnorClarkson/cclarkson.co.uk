import json
import os
from importlib import import_module

from flask import render_template

from app import app
from app import make_routes
from app import settings
from app.tools import helpers


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/cv', methods=['GET'])
def cv():
    return render_template('cv.html', resume=resume)


@app.route('/cv/<string:cv_id>')
def cv_extended(cv_id):
    item = helpers.get_value_from_key('id', cv_id, resume)
    return render_template('blog.html', text=item)


@app.route('/apps', methods=['GET'])
def apps():
    return render_template('apps_landing.html', app_config=app_config)


try:
    with open(os.path.join(settings.APP_STATIC, 'config/app_config.json'))as f:
        app_config = json.load(f)

    with open(os.path.join(settings.APP_STATIC, 'data/resume.json'))as f:
        resume = json.load(f)

    for tool in app_config:
        print(tool)
        importModule = import_module('app.tools.{}'.format(tool['Tool_Name']))
        new_route = make_routes.define_routes(tool, importModule.main)
        app.add_url_rule(rule=tool['Route'],
                         endpoint=tool['Route'],
                         view_func=new_route,
                         methods=["GET", "POST"])
except Exception as e:
    resume = None
    print(e)
