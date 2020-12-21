import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from flask.logging import default_handler
from .config import get_config

from .site import minerclub, db
from .emailer import mail


def create_app(config='product'):
    app = Flask(__name__)

    rot_handler = TimedRotatingFileHandler('logs/MinerClub.log', when='D', backupCount=7)
    rot_handler.setLevel(logging.INFO)
    rot_handler.setFormatter(default_handler.formatter)

    app.logger.addHandler(rot_handler)
    app.logger.addHandler(default_handler)

    app.config.from_object(get_config(config))

    app.register_blueprint(minerclub)
    db.init_app(app)
    mail.init_app(app)

    return app
