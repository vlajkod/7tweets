import logging
from flask import Blueprint, request, jsonify
from seventweets import tweet

tweets = Blueprint('tweets', __name__)
logger = logging.getLogger(__name__)


@tweets.route('/', methods=['GET'])
def get_all():
    return jsonify([t.to_dict() for t in tweet.get_all()])
