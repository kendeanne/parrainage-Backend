"""
Django settings for parrainages project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
#from dotenv import load_dotenv
#import os
import environ

#env = environ.Env()

#environ.Env.read_env()

#DATABASES = {'default': env.db('DATABASE_URL')}

#DEBUG = env.bool('DEBUG', default=False)
#SECRET_KEY = env.str('SECRET_KEY')

# Charge les variables depuis .env
#load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1ryv=$gt9*b=)%nc*p&7gf5ox%kt@44q(+^i8nrh&!+i2fao_c'
#SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False




# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parrainage_backend',
    'rest_framework',
    'rest_framework_simplejwt',
      
]


#from corsheaders.defaults import default_headers
#CORS_ALLOW_HEADERS = list(default_headers) + [
#    "Authorization",
#    "X-Custom-Header",
#]






REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
#CORS_ALLOW_ALL_ORIGINS = True  # Autoriser toutes les origines (peut être restreint)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'parrainage_backend.middleware.PeriodeMiddleware',
]

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["*"]

ROOT_URLCONF = 'parrainages.urls'

#CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


CORS_ALLOWED_ORIGINS = [
    "https://parrainage-frontend-eight.vercel.app",
    
]


CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    ]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Cache-Control'
]






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

WSGI_APPLICATION = 'parrainages.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#DATABASES = {
#    'default': {

       # 'ENGINE': os.getenv('DB_ENGINE'),
        #'NAME': BASE_DIR / 'db.sqlite3',
        #'NAME': os.getenv('DB_NAME'),
        #'USER': os.getenv('DB_USER'),  # Remplace par ton utilisateur MySQL
        #'PASSWORD': os.getenv('DB_PASSWORD'),  # Remplace par ton mot de passe MySQL
        #'HOST': os.getenv('DB_HOST'),  # Laisse 'localhost' si MySQL est en local
        #'PORT': os.getenv('DB_PORT'),  # Port MySQL par défaut
#    }
#}



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgresdb_dgdj',  # Nom de votre DB
        'USER': 'postgresdb_dgdj_user',
        'PASSWORD': 'hMaegjA4ac6sjpGV5oEa7l3fsmwY4yzI',  # Mot de passe Render
        'HOST': 'dpg-cvlf5kogjchc73bmqdr0-a',
        'PORT': '5432',  # Port par défaut
    }
}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#CORS_ALLOWED_ORIGINS = [
#    "https://parrainage-frontend-eight.vercel.app",
#    "http://localhost:4200"
#]


