"""
Django settings for liaozhiMe project.

Generated by 'django-admin startproject' using Django 2.2.20.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _
try:
    from . import localSettings
except Exception as e:
    print('You need to make a copy of localSettingsTemplate file and then make your own configuration and then change the file name to localSettings.')

# what need to be modified in production environment:
# 1. make a copy of localSettinsTempalte and configure it
# 2. change Debug value to False
# 3. add the domian associated with server to ALLOWED_HOST
# 4.(optional) if you use digitalocean cloud server or any other cloud server service that can add external storage to your server and you want to
# place your staticfiles in the external storage, you need to add the dir path to STATICFILES_DIRS and run cmd 'python manage.py collectstatic' to collect
# the static files into staticfiles dir.


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f8xs^ann8$vw$7zzg0qwi^^1vye0#f!692*$==k=4$uz5$^1_^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web.apps.WebConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'liaozhiMe.urls'

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

WSGI_APPLICATION = 'liaozhiMe.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 使用mysql数据库
        'NAME': localSettings.databaseName,  # 要连接的数据库
        'USER': localSettings.databaseAccessedUser,  # 链接数据库的用于名
        'PASSWORD': localSettings.databasePwd,  # 链接数据库的用于名
        'HOST': localSettings.databaseIp,  # mysql服务监听的ip
        'PORT': 3306,  # mysql服务监听的端口
        'ATOMIC_REQUEST': False,  # 设置为True代表同一个http请求所对应的所有sql都放在一个事务中执行
        # (要么所有都成功，要么所有都失败)，这是全局性的配置，如果要对某个
        # http请求放水（然后自定义事务），可以用non_atomic_requests修饰器
        "AUTOCOMMIT": True,  # 全局取消自动提交，慎用
        'OPTIONS': {
            'isolation_level': "read committed",  # 默认为RC，可以设置成其他级别（详见下面解释）
        }
    }
}



# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh'

TIME_ZONE = 'UTC'

USE_I18N = True
LANGUAGES=[
    ('zh',_('Chinese')),
    ('en',_('English'))
]
LOCALE_PATHS=[
    os.path.join(BASE_DIR,'locale')
]
USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/' #this is displaying as the prefix of static file url
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles') #when you collect the static files, it will be collected into this folder
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'web/static')
    ## when I add volumn to my droplet, I need to put all my bilibili resource to this volumn and specify its dir to let django to find it

]
