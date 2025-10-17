"""
Django settings for lannister_news_api project.
"""

from pathlib import Path
import os
import environ


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

# Cargar archivo .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# =========================
# Core / Env
# =========================
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
    "news",
    "chatbot",   # 👈 añadida tu app de chatbot
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lannister_news_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
# Database (AWS RDS MySQL)
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DB", "lannister_news"),
        "USER": os.getenv("MYSQL_USER", "admin"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "root2025"),
        "HOST": os.getenv("MYSQL_HOST", "database-1.cpcimk2ikn91.sa-east-1.rds.amazonaws.com"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "connect_timeout": 60,
            "read_timeout": 60,
            "write_timeout": 60,
        },
    }
}

# =========================
# Cache / Redis
# =========================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# =========================
# Sessions
# =========================
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", 60 * 60 * 24 * 7))
SESSION_SAVE_EVERY_REQUEST = True

# =========================
# DRF
# =========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
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
# Static
# =========================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Custom User
# =========================
AUTH_USER_MODEL = "users.CustomUser"

# =========================
# CORS / CSRF
# =========================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False

# =========================
# MongoDB
# =========================
MONGO_DB = {
    "NAME": os.getenv("MONGO_NAME", "lannister_news"),
    "HOST": os.getenv("MONGO_HOST", "localhost"),
    "PORT": int(os.getenv("MONGO_PORT", "27017")),
    "URI": os.getenv("MONGO_URI", None),
}

# =========================
# News Scraper
# =========================
def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [s.strip() for s in raw.split(",") if s.strip()]

NEWS_SOURCES = _csv_env("NEWS_SOURCES")
NEWS_PROXIES = _csv_env("NEWS_PROXIES")
NEWS_USER_AGENTS = _csv_env("NEWS_USER_AGENTS")

NEWS_REQ_DELAY_MIN = float(os.getenv("NEWS_REQ_DELAY_MIN", "3"))
NEWS_REQ_DELAY_MAX = float(os.getenv("NEWS_REQ_DELAY_MAX", "8"))
NEWS_MAX_RETRIES   = int(os.getenv("NEWS_MAX_RETRIES", "3"))

# =========================
# Chatbot
# =========================

FAQ_PATH = env("FAQ_PATH", default=os.path.join(BASE_DIR, "./chatbot/faqs/faqs.json"))
FAQ_NORMALIZED_PATH = env("FAQ_NORMALIZED_PATH", default=os.path.join(BASE_DIR, "chatbot/faqs/faqs_normalized.json"))
FALLOVER_THRESHOLD = env.float("FALLOVER_THRESHOLD", default=0.08)
FALLOVER_MESSAGE = env("FALLOVER_MESSAGE", default="Lo siento, no entendi xd. Por favor intenta con otra.")
FAQ_MODEL_PATH = env("FAQ_MODEL_PATH", default=os.path.join(BASE_DIR, os.getenv("FAQ_MODEL_PATH", "chatbot/faq_model_2"))) 
