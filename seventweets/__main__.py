import click
from flask.cli import FlaskGroup
from seventweets.app import create_app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """
    Managment script for seventweets service.
    """


if __name__ == '__main__':
    cli()
