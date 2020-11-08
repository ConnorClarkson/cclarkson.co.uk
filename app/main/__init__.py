from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates', static_folder='main_static')

from app.main import routes
