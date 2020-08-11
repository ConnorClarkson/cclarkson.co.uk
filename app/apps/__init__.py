from flask import Blueprint

bp = Blueprint('apps_page', __name__, template_folder='templates', static_folder='apps_static')

from app.apps import routes