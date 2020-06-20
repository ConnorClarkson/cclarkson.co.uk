from flask import Blueprint

bp = Blueprint('blog_page', __name__, template_folder='templates', static_folder='blog_static')

from app.blog_page import routes