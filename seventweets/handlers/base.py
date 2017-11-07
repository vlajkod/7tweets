from flask import Blueprint, current_app, jsonify

base = Blueprint('base', __name__)


@base.route('/')
def index():
    return jsonify({'message': 'Hello world'})
