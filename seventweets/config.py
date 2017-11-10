import os

ST_DB_HOST = 'localhost'
ST_DB_PORT = 5431
ST_DB_USER = '7tweets'
ST_DB_NAME = 'seventweets'
ST_DB_PASS = 'vlajko91'
ST_OWN_NAME = None
ST_OWN_ADDRESS = None
ST_API_TOKEN = None


for name in list(globals().keys()):
    try:
        if name.startswith('ST_'):
            globals()[name] = os.environ[name]
    except KeyError:
        pass
