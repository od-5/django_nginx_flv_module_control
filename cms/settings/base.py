import os

SITE_NAME = 'https://' + os.environ.get('SITE_NAME')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'q%5e*b91-asu&gl-(48n)l8os+r-_)i@3_zq&!l55i$j-$f353'
DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = 'cms.urls'
WSGI_APPLICATION = 'cms.wsgi.application'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
CAM_SECURE_KEY = ''
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
