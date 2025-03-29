import os

LOCAL_SETTINGS = True

from .settings import *
from distutils.util import strtobool

ALLOWED_HOSTS = ['*']

DEBUG = bool(strtobool(os.environ.get('DEBUG')))

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASS = os.environ.get('REDIS_PASSWORD')

BROKER_URL = 'redis://:%s@%s:%s/0' % (REDIS_PASS, REDIS_HOST, REDIS_PORT)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'PORT': '', 
        'CHARSET': 'utf8mb4',
    }
}

CAM_SECURE_KEY = os.environ.get('CAM_SECURE_KEY')
CMD_KEY = os.environ.get('CMD_KEY')
WORK_PATH = os.environ.get('DATA_PATH')
STREAM_ROOT = os.path.join(WORK_PATH, 'hls')

