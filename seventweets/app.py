import sys
import logging
import time
import click
import datetime
import traceback
from flask import Flask, g, current_app
from seventweets import config as configuration
from seventweets.handlers.base import base
from seventweets.handlers.tweets import tweets

LOG_FORMAT = ('%(asctime)-15s %(levelname)s: '
              '%(message)s [%(filename)s:%(lineno)d]')

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
)


logger = logging.getLogger(__name__)


def create_app(_=None):
    """
    Creates and initializes Flask app.

    :return: Created Flask Application.
    """

    app = Flask('seventweets')
    app.config.from_object(configuration)

    app.register_blueprint(base, url_prefix='/')
    app.register_blueprint(tweets, url_prefix='/tweets')
    return app


app = create_app()
