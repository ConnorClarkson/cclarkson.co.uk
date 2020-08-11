from flask import Blueprint

bp = Blueprint('websites', __name__, template_folder='templates', static_folder='website_static')

from app.websites import routes