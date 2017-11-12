import sys
import logging
import time
import click
import datetime
import traceback
from seventweets.utils import generate_api_token
from flask import Flask, g, current_app
from seventweets import config as configuration
from seventweets.handlers.base import base
from seventweets.handlers.tweets import tweets
from seventweets.migrate import MigrationManager

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

    @app.cli.command()
    def config():
        """
        Prints configurations. This includes default values and values provided
        as environment variables.

        These config values can be set by settings environment variables.
        Pattern for environment variables names is to uppercase name of the
        config and prefix it with "ST_". So, "db_name" would be "ST_DB_NAME"
        environment variables.
        """
        cfg = current_app.config.get_namespace('ST_')
        for k, v in cfg.items():
            print(f'{k} = {v}')

    @app.cli.command()
    def generate_token():
        print(generate_api_token())

    @app.cli.command()
    @click.argument('direction', type=click.Choice(['up', 'down']), default='up')
    def migrate(direction):
        """
        Performs database migration.
        """
        MigrationManager().migrate(direction)

    @app.cli.command()
    @click.argument('name', type=str)
    def create_migration(name):
        print(name)
        try:
            MigrationManager().create_migration(name)
        except ValueError as e:
            logger.error('Faild to generate migration: %s', str(e))
            print(str(e))

    return app


app = create_app()
