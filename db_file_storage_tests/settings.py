# -*- coding: utf-8 -*-

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = 'cj33louyit#jhcq%it)swv_(*_b$q%jv5%d8s-hjj#=l=swi^y'
ROOT_URLCONF = 'db_file_storage_tests.urls'
WSGI_APPLICATION = 'db_file_storage_tests.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('database.db')
    }
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

INSTALLED_APPS = (
    'db_file_storage',
    #
    'music',
)

DEFAULT_FILE_STORAGE = 'db_file_storage.storage.DatabaseFileStorage'

TEST_FILES_DIR = os.path.join(BASE_DIR, 'test_files')