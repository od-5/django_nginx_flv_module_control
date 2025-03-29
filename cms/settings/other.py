import os
from distutils.util import strtobool

from .base import BASE_DIR

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../../static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../../media')
STREAM_ROOT = ''

LOGSIZE = 10    # logsize in Mb

LOGFMT_DEFAULT = '%(asctime)s %(levelname)-8s %(filename)s[%(lineno)d]: %(message)s'
LOGFMT_DEBUG = '%(asctime)s %(levelname)-8s %(filename)s %(funcName)s[%(lineno)d]: %(message)s'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': LOGFMT_DEFAULT,
        },
        'debug': {
            # exact format is not important, this is the minimum information
            'format': LOGFMT_DEBUG,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
        },
        'django': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '../../logs/django.log'),
            'backupCount': 1,
            'maxBytes': 1024 * 1024 * LOGSIZE,
            'formatter': 'default',
        },
        'stream': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '../../logs/stream.log'),
            'backupCount': 1,
            'maxBytes': 1024 * 1024 * LOGSIZE,
            'formatter': 'default',
        },
    },
    'loggers': {
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['django'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'stream_log': {
            'handlers': ['stream'],
            'level': 'DEBUG',
        },
        'django.template': {
            'handlers': ['django'],
            'level': 'ERROR'
        }
    }
}
