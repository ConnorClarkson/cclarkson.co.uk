import datetime
import json
import os

from flask import current_app
from flask import render_template

from app.cv_page import bp
from app.tools import helpers

try:
    with open(os.path.join(bp.static_folder, 'data/resume.json'))as f:
        resume = json.load(f)
except Exception as e:
    resume = None
    with open(os.path.join(current_app.config['APP_STATIC'], 'logs/err.log'), "a+") as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tRESUME\t", str(e)]
        f.write(str(error))


@bp.route('/cv', methods=['GET'])
def cv():
    return render_template('cv.html', resume=resume)


@bp.route('/cv/<string:cv_id>')
def cv_extended(cv_id):
    item = helpers.get_value_from_key('id', cv_id, resume)
    return render_template('posts.html', text=item)
