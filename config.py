import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "npsg"
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
