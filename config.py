import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = ''

try:
    from .local import *
except:
    pass

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
