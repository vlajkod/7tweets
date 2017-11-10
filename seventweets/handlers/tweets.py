import logging
from flask import Blueprint, request, jsonify
from seventweets import tweet
from seventweets.exception import error_handler, BadRequest

tweets = Blueprint('tweets', __name__)
logger = logging.getLogger(__name__)


@tweets.route('/', methods=['GET'])
@error_handler
def get_all():
    return jsonify([t.to_dict() for t in tweet.get_all()])


@tweets.route('/<int:tweet_id>', methods=['GET'])
@error_handler
def get_tweet(tweet_id):
    """
    Returns single tweet by ID.
    :param tweet_id: ID of tweet to get.
    """
    return jsonify(tweet.by_id(tweet_id).to_dict())


@tweets.route('/create', methods=['POST'])
@error_handler
def create_tweet():
    """
    Creates new tweet and returns JSON representation.
    """
    body = request.get_json(force=True)
    if 'tweet' not in body:
        raise BadRequest('Invalid body: no "tweets" key in body.')
    content = body['tweet']
    new_tweet = tweet.create(content)
    return jsonify(new_tweet.to_dict()), 201
