import datetime
import json
import os

from flask import current_app, send_from_directory, request
from flask import render_template

from app.main import bp

try:
    with open(os.path.join(current_app.config['APP_STATIC'], 'data/blog.json')) as f:
        blog_json = json.load(f)
except Exception as e:
    blog_json = None
    with open(os.path.join(current_app.config['APP_STATIC'], 'logs/err.log'), "a+") as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tBLOG\t", str(e)]
        f.write(str(error))


@bp.route('/')
def index():
    return render_template('index.html', blog=blog_json)


@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
@bp.route('/favicon.ico')
def static_from_root():
    return send_from_directory(current_app.config['APP_STATIC'], request.path[1:])