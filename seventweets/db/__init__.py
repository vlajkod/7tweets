import logging
import abc
import os
from typing import Tuple, TypeVar
from importlib import import_module

from datetime import datetime

# type for type hinting
_T = TypeVar('_T')

TwResp = Tuple[int, str, str, datetime, datetime, str]

logger = logging.getLogger(__name__)

TWEET_COLUMN_ORDER = 'id, tweet, type, created_at, modified_at, reference'


class Operations(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def get_all_tweets(cursor):
        """
        Returns all tweets from database.
        :param cursor: Database cursor.
        :return: All tweets from database.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_tweet(id_: int, cursor):
        """
        Returns single tweets from database.

        :param id_: ID of tweet to get.
        :param cursor: Database cursor.
        :return: Tweet with provided ID.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def insert_tweet(tweet: str, cursor):
        """
        Inserts new tweet and returns id of the created row.
        :param tweet: Content of the tweet to add.
        :param cursor: Database cursor.
        :return: ID of tweet that was created.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def modify_tweet(id_: int, new_content: str, cursor) -> TwResp:
        """
        Updates tweet content
        :param id_: ID of tweet to update.
        :param new_content: New tweet content.
        :param cursor: Database cursor.
        :return: ID of tweet that was updated, if tweet with provided ID was found, None otherwise.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def delete_tweet(id_: int, cursor) -> bool:
        """
        Deletes tweet with provided ID from database.

        :param id_: ID of tweet to delete.
        :param cursor: Database cursor.
        :return: Boolean indicating if tweet with ID was deleted. (False if tweet does not exist).
        """
        raise NotImplementedError()


default_bakcend = os.getenv('ST_DB_BACKEND', 'memory')


def get_db(backend=default_bakcend):
    """
    Opens a new database connection if there is none yet for
    the current application context.
    """
    backend_module = import_module(f'seventweets.db.backends.{backend}')
    return backend_module.Database()


def get_ops(backend=default_bakcend) -> Operations:
    backend_module = import_module(f'seventweets.db.backends.{backend}')
    return backend_module.Operations()
