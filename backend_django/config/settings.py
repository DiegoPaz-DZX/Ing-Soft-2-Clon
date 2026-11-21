import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "kyzen-clave-solo-para-desarrollo")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "balance",
    "categorias",
    "tips",
    "usuarios",
    "alertas",
    "historial",
    "sesion",
    "recomendaciones",
    "preferencias",
    "reportes",
    "metas",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = False
USE_TZ = True
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
TIPO_CAMBIO_URL = "https://open.er-api.com/v6/latest/USD"
TIPO_CAMBIO_SOLES_POR_DOLAR = "3.75"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")
