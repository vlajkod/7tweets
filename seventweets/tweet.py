import logging
from datetime import datetime
from functools import partial
from seventweets.db import get_db, get_ops
from seventweets.exception import NotFound, BadRequest
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


def by_id(id_):
    """
    Returns tweet with provided ID.
    :param int id_: ID of tweet to get.
    :raises NotFound: If tweet with provided ID was not founc.
    """
    res = get_db().do(partial(get_ops().get_tweet, id_))
    if res is None:
        raise NotFound(f'Tweet with id: {id_} not found.')
    return Tweet(*res)


def create(content):
    """
    Creates new tweet with provided content.
    :param content: Tweet content.
    :return: Tweet
    """
    check_length(content)
    return Tweet(*get_db().do(partial(get_ops().insert_tweet, content)))


def modify(id_, new_content):
    """
    Modifies tweet with provided new content.
    :param id_: ID of tweet to modify.
    :param new_content: New content for tweet.
    :return: Modified tweet.
    """
    check_length(new_content)
    updated = get_db().do(partial(get_ops().modify_tweet, id_, new_content))
    if not updated:
        raise NotFound(f'Tweet for ID: {id_} not found.')
    return Tweet(*updated)


def delete(id_):
    """
    Removes tweet with provided ID from database.
    :param id_: ID of tweet to delete.
    :raises: NotFound if tweet with provided ID not found.
    """
    deleted = get_db().do(partial(get_ops().delete_tweet, id_))
    if not deleted:
        raise NotFound(f'Tweet with provided id: {id_} not found.')
    return deleted


def check_length(tweet):
    """
    Verifies if provided tweet content is less than 140 characters.

    :param str tweet: Tweet content to check.
    :raises: BadRequest: If tweet content is longer then 140 characters.
    """
    if len(tweet) > 140:
        raise BadRequest('Tweet length exceeds 140 characters.')
