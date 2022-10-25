import os
from pathlib import Path

import environ
from django.contrib.messages import constants as messages

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = 'nt(o48x3+qoygx!*=$==ul!&^4nyr8c%ybpga1p^as##_3s3__'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'category',
    'store',
    'carts',
    'accounts',
    'orders',
    'payments',
    'paypal.standard.ipn',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'greatkart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'greatkart.wsgi.application'

AUTH_USER_MODEL = 'accounts.Account'  # Tên model thay thế cho model user mặc định

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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
USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    'greatkart/static'
]

# Cầu hình media file
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.WARNING: 'warning',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.DEBUG: 'secondary'
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
LANGUAGE_CODE = 'vi'
VNPAY_RETURN_URL = 'http://localhost:8000/payments/VNpayment_return'  # get from config
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # get from config
VNPAY_API_URL = 'https://sandbox.vnpayment.vn/merchant_webapi/merchant.html'
VNPAY_TMN_CODE = '5GLQM2TS'  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = 'MEEKSSJGWYVUQWICIRIMCELEPFRVKPGM'  # Secret key for create checksum,get from config
PAYPAL_RECEIVER_EMAIL = 'XXXXX'
PAYPAL_TEST = True
MOMO_RETURN_URL = 'http://localhost:8000/payments/MoMo_payment_return'  # get from config