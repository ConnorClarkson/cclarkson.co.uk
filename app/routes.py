import datetime
import json
import os
import csv
from importlib import import_module

from flask import render_template

from app import app
from app import make_routes
from app import settings
from app.tools import helpers


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', blog=blog)


@app.route('/')
@app.route('/blog')
def blog():
    return render_template('blog.html', blog=blog)


@app.route('/cv', methods=['GET'])
def cv():
    return render_template('cv.html', resume=resume)


@app.route('/cv/<string:cv_id>')
def cv_extended(cv_id):
    item = helpers.get_value_from_key('id', cv_id, resume)
    return render_template('posts.html', text=item)


@app.route('/blog/<string:post_id>')
def blog_extended(post_id):
    item = helpers.get_value_from_key('id', post_id, blog)
    return render_template('blog_posts.html', text=item)


@app.route('/test')
def test():
    csv_string = {}
    with open(os.path.join(settings.APP_STATIC, 'test/data.csv'))as f:
        c = csv.reader(f)
        for row in c:
            if row[0] in csv_string:
                if row[1] in csv_string[row[0]]:
                    csv_string[row[0]][row[1]] += int(row[2])
                else:
                    csv_string[row[0]][row[1]] = int(row[2])
            else:
                csv_string[row[0]] = {}
                csv_string[row[0]][row[1]] = int(row[2])
    tmp_arr =[]
    for sender in csv_string:
        for receiver in csv_string[sender]:
            tmp_arr.append([sender,receiver, csv_string[sender][receiver]])
    return render_template('test.html', csv_file=tmp_arr)


@app.route('/apps', methods=['GET'])
def apps():
    return render_template('apps_landing.html', app_config=app_config)


try:
    with open(os.path.join(settings.APP_STATIC, 'config/app_config.json'))as f:
        app_config = json.load(f)

    for tool in app_config:
        importModule = import_module('app.tools.{}'.format(tool['Tool_Name']))
        new_route = make_routes.define_routes(tool, importModule.main)
        app.add_url_rule(rule=tool['Route'],
                         endpoint=tool['Route'],
                         view_func=new_route,
                         methods=["GET", "POST"])
except Exception as e:
    with open(os.path.join(settings.APP_STATIC, 'logs/err.log', "a+")) as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tAPP CONFIG\t", str(e)]
        f.write(str(error))

try:
    with open(os.path.join(settings.APP_STATIC, 'data/resume.json'))as f:
        resume = json.load(f)
except Exception as e:
    resume = None
    with open(os.path.join(settings.APP_STATIC, 'logs/err.log', "a+")) as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tRESUME\t", str(e)]
        f.write(str(error))

try:
    with open(os.path.join(settings.APP_STATIC, 'data/blog.json')) as f:
        blog = json.load(f)
except Exception as e:
    blog = None
    with open(os.path.join(settings.APP_STATIC, 'logs/err.log', "a+")) as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tBLOG\t", str(e)]
        f.write(str(error))
