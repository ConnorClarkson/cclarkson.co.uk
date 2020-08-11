import json
import os
from datetime import datetime

from flask import render_template, current_app

from app.websites import bp

try:
    with open(os.path.join(current_app.config['APP_STATIC'], 'data/blog.json')) as f:
        blog_json = json.load(f)
except Exception as e:
    blog_json = None
    with open(os.path.join(current_app.config['APP_STATIC'], 'logs/err.log'), "a+") as f:
        error = [datetime.now().strftime("%d-%m-%Y %H:%M"), "\tBLOG\t", str(e)]
        f.write(str(error))

@bp.route('/showcase', methods=['GET'])
def showcase():
    websites =[]
    for key in blog_json:
        if blog_json[key]['type'] == "website":
            websites.append(blog_json[key])

    return render_template('websites.html', websites=websites)
