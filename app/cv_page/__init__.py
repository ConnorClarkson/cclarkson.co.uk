from flask import Blueprint

bp = Blueprint('cv_page', __name__, template_folder='templates', static_folder='cv_static')

from app.cv_page import routes
