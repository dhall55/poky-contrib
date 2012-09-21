# Django settings for webHob project.
import os
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_webhob',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

#MANAGEMENT_SERV_URL = 'http://10.239.47.36:8001'
MANAGEMENT_SERV_URL = 'http://localhost:8001'

FILE_SERV_INTERFACE = ('10.239.47.176', 30004)
UPLOAD_FILE_SERV_UID = 'ftpuser'
UPLOAD_FILE_SERV_PW = '123456'
LAYER_UPLOAD_DIR = '/home/builder/nfsroot'

STATICFILES_DIRS = (
     os.path.join(os.path.dirname(__file__), 'static').replace('\\','/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = '0fgip^7zf$h$ypwq+mss@n%!h(ct7y+g4x8uw=rg!sj253i^@s'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'webHob.urls'
TEMPLATE_DIRS = (
     os.path.join(os.path.dirname(__file__), 'template').replace('\\','/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hob.operators',
    'hob.projects',
    'hob.groups',
    'hob.builds',
    'hob.recipe',
    'hob.package',
)
