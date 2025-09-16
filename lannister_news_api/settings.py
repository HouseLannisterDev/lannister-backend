"""
Django settings for lannister_news_api project.
"""

from pathlib import Path
import os

# =========================
# Paths & Core
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-!uwquq*ppxw@0c67nzmvvcm&tzd2mmtkgzjrxr$r0c1i=1%d2-",
)
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# =========================
# Installed Apps
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",

    # Local
    "users",
    "news",  # app para scraping + Mongo
    "chatBot",  # app para chatbot con IA
]

# =========================
# Middleware (orden importa)
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS lo más arriba posible tras SessionMiddleware
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",

    # CSRF después de CommonMiddleware
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lannister_news_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # opcional
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

WSGI_APPLICATION = "lannister_news_api.wsgi.application"

# =========================
# Database (MySQL)
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DB", "lannister_news"),
        "USER": os.getenv("MYSQL_USER", "lannister_user"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "lannister_pwd"),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# =========================
# Cache / Redis
# =========================
# Requiere: pip install django-redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # Si usas Redis Cloud, pon REDIS_URL con credenciales
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": os.getenv("REDIS_PASSWORD", ""),  # si tu redis tiene clave
        },
    }
}

# =========================
# Sessions (persistentes con Redis)
# =========================
# Usa Redis como cache + fallback en DB (tabla django_session)
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", 60 * 60 * 24 * 7))  # 7 días
SESSION_SAVE_EVERY_REQUEST = True

# =========================
# DRF
# =========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",   # sesiones vía cookie
        # "rest_framework.authentication.BasicAuthentication",   # opcional para pruebas Postman
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # ajústalo luego
    ],
    # Si quieres sólo JSON en prod, puedes forzar renderers aquí.
    # "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# =========================
# Password validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# i18n / TZ
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# =========================
# Static files
# =========================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # útil para collectstatic en prod
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Custom User Model
# =========================
AUTH_USER_MODEL = "users.CustomUser"

# =========================
# CORS / CSRF
# =========================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True  # importante para cookies

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False  # el front debe leerla para enviar X-CSRFToken

# =========================
# Seguridad (activa en producción)
# =========================
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SAMESITE = "Lax"  # o "Strict" según tu UX

# =========================
# MongoDB (para app news)
# =========================
# Si usas Mongo Atlas, define MONGO_URI y omite HOST/PORT/NAME.
MONGO_DB = {
    "NAME": os.getenv("MONGO_NAME", "lannister_news"),
    "HOST": os.getenv("MONGO_HOST", "localhost"),
    "PORT": int(os.getenv("MONGO_PORT", "27017")),
    "URI": os.getenv("MONGO_URI", None),
}

# =========================
# News Scraper settings
# =========================

def _csv_env(name: str, default: str = "") -> list[str]:
    """
    Lee una variable de entorno separada por comas y devuelve una lista limpia
    (sin espacios ni elementos vacíos).
    """
    raw = os.getenv(name, default)
    return [s.strip() for s in raw.split(",") if s.strip()]

# Dominios a scrapear (vienen del .env NEWS_SOURCES)
NEWS_SOURCES = _csv_env("NEWS_SOURCES")

# Proxies (si no tienes reales, deja NEWS_PROXIES vacío en .env)
NEWS_PROXIES = _csv_env("NEWS_PROXIES")

# Rotación de User-Agents (si no pones, usamos un fallback interno del scraper)
NEWS_USER_AGENTS = _csv_env("NEWS_USER_AGENTS")

# Delays entre requests (segundos) y reintentos
NEWS_REQ_DELAY_MIN = float(os.getenv("NEWS_REQ_DELAY_MIN", "3"))
NEWS_REQ_DELAY_MAX = float(os.getenv("NEWS_REQ_DELAY_MAX", "8"))
NEWS_MAX_RETRIES   = int(os.getenv("NEWS_MAX_RETRIES", "3"))
