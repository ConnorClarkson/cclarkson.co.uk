import datetime
import json
import os

from flask import current_app
from flask import render_template

from app.blog_page import bp

try:
    with open(os.path.join(bp.static_folder, 'data/blog.json')) as f:
        blog_json = json.load(f)
except Exception as e:
    blog_json = None
    with open(os.path.join(current_app.config['APP_STATIC'], 'logs/err.log'), "a+") as f:
        error = [datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "\tBLOG\t", str(e)]
        f.write(str(error))


@bp.route('/blog')
def blog():
    return render_template('blog.html', blog=blog_json)


@bp.route('/blog/<string:post_id>')
def blog_extended(post_id):
    item = blog_json[post_id]
    return render_template('blog_posts.html', text=item)
