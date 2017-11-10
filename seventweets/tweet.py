import logging
from datetime import datetime
from functools import partial
from seventweets.db import get_db, get_ops
logger = logging.getLogger(__name__)


class Tweet:
    """
    Tweet model holding information about single tweet and providing operations
    on single tweet and multiple tweets. (batch)
    """
    def __init__(self, id_, tweet, type_, created_at, modified_at, reference=None):
        self.id = id_
        self.tweet = tweet
        self.type = type_
        self.created_at = created_at
        self.modified_at = modified_at
        self.reference = reference

    def to_dict(self):
        """
        Converts tweet to dictionary. Optionals filed may not exist in resulting dictionary.
        :return: Tweet represented as dictionary
        """
        r = {
            'id': self.id,
            'type': self.type,
            'tweet': self.tweet,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }
        return r

    @classmethod
    def from_dict(cls, tweet_dict):
        try:
            id_ = tweet_dict['id']
            tweet = tweet_dict['tweet']
            type_ = tweet_dict['type']
            created_at = datetime.strftime(
                tweet_dict['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            modified_at = datetime.strftime(
                tweet_dict['modified_at'], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            return cls(id_, tweet, type_, created_at, modified_at, None)
        except KeyError:
            raise ValueError('Invalid format of tweet dict provided.')


def get_all():
    """
    Returns list of all tweets.
    :return: [Tweet]
    """
    return [Tweet(*args) for args in get_db().do(get_ops().get_all_tweets)]


def create(content):
    """
    Creates new tweet with provided content.
    :param content: Tweet content.
    :return: Tweet
    """
    return Tweet(*get_db().do(partial(get_ops().insert_tweet, content)))
