import os

from flask import Flask

from app import settings

app = Flask(__name__)
with open(os.path.join(settings.APP_ROOT, 'static/KEYS/secret_key')) as f:
    key = f.read()
app.secret_key = key

#login_manager = LoginManager()
#login_manager.init_app(app)

from app import login
from app import routes