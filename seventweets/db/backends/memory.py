import logging
import itertools
from datetime import datetime
from collections import namedtuple
from typing import Iterable, Optional, List, Dict

from seventweets import db

from seventweets.db import (
    TwResp, TWEET_COLUMN_ORDER
)

logger = logging.getLogger(__name__)

Tweet = namedtuple('Tweet', TWEET_COLUMN_ORDER)


class Database:
    """
    In-memory storage for :class `Operations`.
    """

    def __init__(self):
        self.tweets = list()
        self.counter = itertools.count()

    def test_connection(self):
        pass

    def close(self):
        pass

    def do(self, fn):
        """
        Executes provided fn and gives it a storage to work with.
        :param fn:
            Function to execute.
            It has to accept one arguments, the :class: `Database` instance.
        :return: Whatever `fn` returns.
        """
        return fn(self)


class Operations(db.Operations):
    @staticmethod
    def insert_tweet(tweet: str, storage: Database):
        now = datetime.now()
        new_tweet = Tweet(
            id=next(storage.counter), tweet=tweet, type='original',
            created_at=now, modified_at=now, reference=''
        )
        storage.tweets.append(new_tweet)

    @staticmethod
    def get_all_tweets(storage: Database):
        return storage.tweets

    @staticmethod
    def get_tweet(id_: int, storage: Database):
        for tweet in storage.tweets:
            if tweet.id == id_:
                return tweet
        else:
            raise KeyError(f'Tweet with id={id_} not found.')

    @staticmethod
    def delete_tweet(id_: int, storage: Database):
        try:
            storage.tweets.remove(Operations.get_tweet(id_, storage))
            return True
        except KeyError:
            return False

    @staticmethod
    def modify_tweet(id_: int, new_content: str, storage: Database) -> TwResp:
        tweet = Operations.get_tweet(id_, storage)
        assert tweet.type == 'original'
        new_tweet = Tweet(
            id=tweet.id, tweet=new_content, type=tweet.type,
            created_at=tweet.created_at, modified_at=tweet.modified_at
        )
        storage.tweets.remove(tweet)
        storage.tweets.append(new_tweet)
        return new_tweet
