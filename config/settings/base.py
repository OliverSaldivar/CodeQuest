"""
Configuracion base del proyecto CodeQuest.
Sincroniza PostgreSQL, SimpleJWT con llave primaria personalizada (id_estudiante)
y el directorio global de plantillas en la raiz del proyecto.
"""
import os
from datetime import timedelta
from pathlib import Path

# Se usan tres niveles .parent para apuntar a la raiz del proyecto (Defecto 3 CU-03 / CU-04)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-codequest-dream-team-mvp-2026-key"
)

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "apps.core",
    "apps.accounts",
    "apps.curriculum",
    "apps.challenges",
    "apps.gamification",
    "apps.analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "codequest_db"),
        "USER": os.environ.get("POSTGRES_USER", "codequest_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "codequest_password"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Configuracion explicita de SimpleJWT para llave primaria id_estudiante (Defecto 1 CU-04)
DURACION_TOKEN_ACCESO_HORAS = 8
DURACION_TOKEN_REFRESCO_DIAS = 7

SIMPLE_JWT = {
    "USER_ID_FIELD": "id_estudiante",
    "USER_ID_CLAIM": "id_estudiante",
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=DURACION_TOKEN_ACCESO_HORAS),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=DURACION_TOKEN_REFRESCO_DIAS),
}

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
