import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    SECRET_KEY = '9823cr03y34894rvmu43!'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SCUTWORK_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    SUBMISSIONS_SAVE_PATH = os.path.join(basedir, 'submissions')
    SCUTWORK_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
#    SESSION_COOKIE_SAMESITE = 'Strict'
#    SESSION_COOKIE_SECURE = True
    SCUTWORK_DOMAIN_NAME = 'scutwork.mzp.icu'
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    AVATARS_SAVE_PATH = os.path.join(SCUTWORK_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (24, 100, 200)
    AVATARS_CROP_BASE_WIDTH = 320
    QUIZ_PASSING_SCORE = 80


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///" + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

