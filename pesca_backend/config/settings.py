"""
Django settings for config project.
"""

from pathlib import Path
import dj_database_url
import os
from google.oauth2 import service_account
import json

BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================
# SECURITY
# ===============================

SECRET_KEY = 'django-insecure-j93hfgt&=^qj^5sa9eic2$=43q=e-8z*s$ku2ddxuw9o0&=05i'

DEBUG = True

ALLOWED_HOSTS = ["*"]


# ===============================
# APPLICATIONS
# ===============================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "storages",
    "rest_framework",

    "clubs",
    "users",
    "contests",
]


# ===============================
# MIDDLEWARE
# ===============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ===============================
# TEMPLATES
# ===============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ===============================
# DATABASE
# ===============================

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600
    )
}


# ===============================
# PASSWORD VALIDATION
# ===============================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ===============================
# INTERNATIONALIZATION
# ===============================

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True
USE_TZ = True


# ===============================
# STATIC FILES
# ===============================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ===============================
# GOOGLE CLOUD STORAGE (MEDIA)
# ===============================

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

GS_BUCKET_NAME = "fishcall-media"

if "SERVICE_ACCOUNT_JSON" in os.environ:

    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    )

else:

    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR, "credentials/service_account.json")
    )

GS_PROJECT_ID = "grand-signifier-471712-m5"
GS_DEFAULT_ACL = None
GS_FILE_OVERWRITE = False


# URL pública de media
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"


# ===============================
# PUSH NOTIFICATIONS (VAPID)
# ===============================

VAPID_PUBLIC_KEY = "BKKhCCYEJzpW2s1_qcMN4cLwwXdQsxwKh4XrILvH-ad5Rt4i8_rIZY-yl3LrbjR4C33wyywGBH9b9pH_yIzB54c="
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgM06Jw2_D_9__BL5Tgwu3wxX1xIqWW4V5hmFdjz8T3a2hRANCAASioQgmBCc6VtrNf6nDDeHC8MF3ULMcCoeF6yC7x_mneUbeIvP6yGWPspdy6240eAt98MssBgR_W_aR_8iMweeH"
VAPID_ADMIN_EMAIL = "admin@fishcall.com"


# ===============================
# DEFAULT PRIMARY KEY
# ===============================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MERCADOPAGO_ACCESS_TOKEN = "APP_USR-1697937262543059-031100-762e8c7705f7e1198ca2851901c42bc3-3258945590"
