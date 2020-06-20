from app.apps import bp
from flask import current_app
import datetime
import json
import os
from importlib import import_module
from flask import render_template
from app import make_routes


@bp.route('/apps_landing', methods=['GET'])
def apps_landing():
    return render_template('apps_landing.html', app_config=app_config)




try:
    with open(os.path.join(current_app.config['APP_STATIC'], 'config/app_config.json'))as f:
        app_config = json.load(f)

    for tool in app_config:
        importModule = import_module('app.tools.{}'.format(tool['Tool_Name']))
        new_route = make_routes.define_routes(tool, importModule.main)
        bp.add_url_rule(rule=tool['Route'],
                         endpoint=tool['Route'],
                         view_func=new_route,
                         methods=["GET", "POST"])
except Exception as e:
    with open(os.path.join(current_app.config['APP_STATIC'], 'logs/err.log'), "a+") as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tAPP CONFIG\t", str(e)]
        f.write(str(error))



