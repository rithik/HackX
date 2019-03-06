import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    try:
        try:
            if os.environ['FLASK_ENV'] == "development":
                import settings
                SECRET_KEY = settings.SECRET_KEY
        except:
            SECRET_KEY = os.environ['SECRET_KEY']
    except:
        import settings
        SECRET_KEY = settings.SECRET_KEY

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
