import logging
from datetime import datetime
from functools import partial
from seventweets.db import get_db, get_ops
from seventweets.exception import NotFound, BadRequest
from typing import List

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


def retweet(server, id_):
    """
    Creates retweet of original tweet.
    :param server: Server name that holds original tweet.
    :param id_: ID of tweet on original server.
    :return: Newly created tweet.
    :rtype: Tweet
    """
    return Tweet(*get_db().do(partial(get_ops().create_retweet, server, id_)))


def search(content: str=None,
           created_from: datetime=None,
           created_to: datetime=None,
           modified_from: datetime=None,
           modified_to: datetime=None,
           retweets: bool=None,
           all: bool=False) -> List[Tweet]:
    """
    Performs search on tweets and returns list of results.
    If no parameters are provided, this will yield same results as listing tweets.

    :param content: Content to search in tweet.
    :param created_from: Start time for tweet creation.
    :param created_to: End time for tweet creation.
    :param modified_from: Start time for tweet modification.
    :param modified_to: End time for tweet modification.
    :param retweets: Flag indication if retweet or original tweets should be searched.
    :param all: Flag indication if all nodes should be searched or only this one.
    :return: Result searching tweets.
    :rtype: [Tweet]
    """
    search_fun = partial(get_ops().search_tweets, content, created_from, created_to,
                         modified_from, modified_to, retweets)
    res = [Tweet(*args) for args in get_db().do(search_fun)]
    if all:
        others_res = search_others(content, created_from, created_to,
                                   modified_from, modified_to, retweets)
        res.extend(others_res)
    return res


def search_others(content: str=None,
           created_from: datetime=None,
           created_to: datetime=None,
           modified_from: datetime=None,
           modified_to: datetime=None,
           retweets: bool=None,
           all: bool=False):
    return []


def check_length(tweet):
    """
    Verifies if provided tweet content is less than 140 characters.

    :param str tweet: Tweet content to check.
    :raises: BadRequest: If tweet content is longer then 140 characters.
    """
    if len(tweet) > 140:
        raise BadRequest('Tweet length exceeds 140 characters.')


def count(type_: str=None):
    """
    Returns number of tweets in database. If `separate` is True, two values
    are returned. First is number of original tweets and second is number of
    retweets.

    If `separate` is False (default) only one number is returned.
    :param type_: Type of tweets to count. Valid values are 'original' and 'retweet'.
    """
    return get_db().do(partial(get_ops().count_tweets, type_))
