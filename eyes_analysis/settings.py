import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open('eyes_analysis/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()


DEBUG = True

ALLOWED_HOSTS = ['retina.ssmu.ru', '172.24.200.72', '127.0.0.1', '172.21.0.3','172.21.0.2']

INSTALLED_APPS = [
    'home',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'api',
    'multiselectfield',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eyes_analysis.urls'

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
                'django.template.context_processors.media'
            ],
        },
    },
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'volumes/db.sqlite3',
    }
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = None


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Novosibirsk'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = 'orthanc_db/'
MEDIA_ROOT = os.path.join(BASE_DIR, "orthanc_db")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1
CSRF_TRUSTED_ORIGINS = ['https://retina.ssmu.ru/*', 'http://172.24.200.72/*','http://172.21.0.3/*', 'http://172.21.0.2/*']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logging/debug.log",
            'formatter': 'standard',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    "loggers": {
        "django": {
            "handlers": ['console', 'file'],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Определение пути и имени файла для логов
log_file = "logging/debug.log"

# Создание логгера
logger = logging.getLogger('error_logger')
logger.setLevel(logging.ERROR)

# Создание обработчика для записи в файл
handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
handler.setLevel(logging.ERROR)

# Определение формата записи логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(handler)
