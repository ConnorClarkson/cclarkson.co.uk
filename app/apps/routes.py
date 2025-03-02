import datetime
import json
import os
from importlib import import_module

from flask import current_app
from flask import render_template

from app import make_routes
from app.apps import bp


@bp.route('/apps_landing', methods=['GET'])
def apps_landing():
    return render_template('apps_landing.html', app_config=enabled_apps)


try:
    with open(os.path.join(bp.static_folder, 'config/app_config.json'))as f:
        app_config = json.load(f)
    enabled_apps = []
    for tool in app_config:
        if tool['enabled']:
            enabled_apps.append(tool)
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
