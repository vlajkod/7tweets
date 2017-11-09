from fabric.api import local, run, env, settings


env.user = 'root'
env.hosts = ['try.sedamcvrkuta.com:22202']

network_name = '7tweets'
image_tag = 'vlajko/7tweets'
db_container_name = '7tweets-postgres'
db_user = '7tweets'
db_name = 'seventweets'
db_port = 5431
db_image = 'postgres:9.6.2'
db_volume = 'postgres-7tweets-data'

gunicorn_port = 8080
external_port = 80

service_container_name = 'seventweets'


def create_network():
    """
    Creates network for communication between different docker containers
    needed for seventweets to work. If network already exist, this command
    not fail.
    """
    with settings(warn_only=True):
        local(f'docker network create {network_name}')


def create_volume():
    """
    Creates volume for data storage for postgres DB. If volume already exist,
    it will kept and command will not fail.
    """
    with settings(warn_only=True):
        local(f'docker volume create {db_volume}')


def start_db(db_pass):
    """
    Starts postgres database. If database is already running, it will keep running.
    :param db_pass: Database user to use.
    """
    with settings(warn_only=True):
        local(f'docker run -d --name {db_container_name} --net {network_name} '
              f'-v {db_volume}:/var/lib/postgresql/data '
              f'--restart unless-stopped -e POSTGRES_USER={db_user} '
              f'-e POSTGRES_PASSWORD={db_pass} '
              f'-e POSTGRES_DB={db_name} '
              f'-p 127.0.0.1:5431:5432 {db_image}')

