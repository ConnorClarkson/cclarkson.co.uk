import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config

bootstrap = Bootstrap()


def create_app(config_class=Config):
    application = Flask(__name__)

    application.config.from_object(config_class)

    bootstrap.init_app(application)

    from app.errors import bp as errors_bp
    application.register_blueprint(errors_bp)

    with application.app_context():
        from app.main import bp as main_bp
        application.register_blueprint(main_bp)

    with application.app_context():
        from app.blog_page import bp as blog_bp
        application.register_blueprint(blog_bp)

    with application.app_context():
        from app.cv_page import bp as cv_bp
        application.register_blueprint(cv_bp)

    with application.app_context():
        from app.apps import bp as app_bp
        application.register_blueprint(app_bp, url_prefix='/apps')

    with application.app_context():
        from app.websites import bp as web_bp
        application.register_blueprint(web_bp)

    @application.template_filter('datetimeformat')
    def datetimeformat(value):
        return datetime.fromtimestamp(value, tz=timezone.utc).strftime('%d/%m/%Y %-I:%M%p')

    @application.template_filter('datetimeHMformat')
    def datetimeHMformat(value):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
        dts = dt.strftime('%Y-%m-%d %H:%M')
        return dts

    if not application.debug and not application.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/cclarkson.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        application.logger.addHandler(file_handler)

        application.logger.setLevel(logging.INFO)
        application.logger.info('Microblog startup')

    return application
