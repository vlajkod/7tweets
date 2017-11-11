import logging
import pg8000

from datetime import datetime
from typing import Optional, Iterable, List, Union, Callable

from flask import current_app
from seventweets import db
from seventweets.db import (
    TwResp, _T, TWEET_COLUMN_ORDER
)


logger = logging.getLogger(__name__)
DbCallback = Callable[[pg8000.Cursor], _T]


class Database(pg8000.Connection):
    """
    Thin wrapper around `pg8000.Connection` that allows executing queries
    on database and makes sure that connection is in valid state by
    performing commit and rollback when appropriate.
    """

    def __init__(self):
        super(Database, self).__init__(
            user=current_app.config['ST_DB_USER'],
            host=current_app.config['ST_DB_HOST'],
            unix_sock=None,
            port=int(current_app.config['ST_DB_PORT']),
            database=current_app.config['ST_DB_NAME'],
            password=current_app.config['ST_DB_PASS'],
            ssl=False,
            timeout=None
        )

    def test_connection(self):
        """
        Performs trivial query on database to check if connections is successful.
        If not, this will raise exception.
        """
        try:
            self.do(lambda cur: cur.execute('SELECT 1'))
        except Exception:
            logger.critical('Unable to execute query on database.')
            raise

    def cleanup(self):
        try:
            self.close()
        except pg8000.core.InterfaceError:
            # this exception is raised if db is already closed, which will happen if class is used as context manager
            pass

    def do(self, fn: DbCallback) -> _T:
        """
        Executes provided fn and gives it cursor to work with.

        Cursor will automatically be closed after, no matter that result of
        execution is. Returns value is whatever `fn` returns.

        After each operation, commit is performed if no exception is raised.
        If exception is raised - transaction is rolled back.
        :param fn: Function to execute. It has to accept one argument, cursor that it will use to
        communicate with database.
        :return: Whatever `fn` returns
        """
        cursor = self.cursor()
        try:
            res = fn(cursor)
            self.commit()
            return res
        except Exception:
            self.rollback()
            raise
        finally:
            cursor.close()


class Operations(db.Operations):

    @staticmethod
    def get_all_tweets(cursor: pg8000.Cursor) -> Iterable[TwResp]:
        """
        Returns all tweet from database.

        :param cursor: Database cursor.
        :return: All tweets from database.
        """
        cursor.execute(f'''
            SELECT {TWEET_COLUMN_ORDER} 
            FROM tweets
            ORDER BY created_at DESC;
        ''')
        return cursor.fetchall()

    @staticmethod
    def get_tweet(id_: int, cursor: pg8000.Cursor) -> TwResp:
        """
        Returns single tweet from database.

        :param id_: ID of tweet to get.
        :param cursor: Database cursor.
        :return: Tweet with provided ID.
        """
        cursor.execute(f'''
            SELECT {TWEET_COLUMN_ORDER}
            FROM tweets
            WHERE id=(%s)
        ''', (id_,))
        return cursor.fetchone()

    @staticmethod
    def insert_tweet(tweet: str, cursor: pg8000.Cursor) -> TwResp:
        """
        Inserts new tweet and returns id of the created row.
        :param tweet: Content of the tweet to add.
        :param cursor: Database cursor.
        :return: ID of tweet that was created.
        """
        cursor.execute(f'''
            INSERT INTO tweets (tweet) VALUES (%s)
            RETURNING {TWEET_COLUMN_ORDER};
        ''', (tweet,))
        return cursor.fetchone()

    @staticmethod
    def modify_tweet(id_: int, new_content: str, cursor: pg8000.Cursor) -> TwResp:
        """
        Updates tweet content.

        :param id_: Id of tweet to update.
        :param new_content: New tweet content.
        :param cursor: Database cursor.
        :return: Tweet that was update, if tweet with provided ID was found, None otherwise
        """
        cursor.execute(f'''
            UPDATE tweets SET tweet=%s, modified_at=%s
            WHERE id = (%s)
            RETURNING {TWEET_COLUMN_ORDER};
        ''', (new_content, datetime.utcnow(), id_))
        return cursor.fetchone()

    @staticmethod
    def delete_tweet(id_: int, cursor: pg8000.Cursor) -> bool:
        """
        Deletes tweet with provided ID from database.
        :param id_: ID of tweet to delete.
        :param cursor: Database Cursor
        :return: Boolean indicating if tweet with ID was deleted (False if tweet does not exist.
        """
        cursor.execute(f'''
            DELETE FROM tweets
            WHERE id=%s
        ''', (id_,))
        return cursor.rowcount > 0
