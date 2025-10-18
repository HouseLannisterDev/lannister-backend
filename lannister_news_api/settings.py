###############################
# FINAL CORS / CSRF / COOKIES #
###############################
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://develop.d168j68zix66ce.amplifyapp.com",
    "https://lannister-news.com",
    "https://app.lannister-news.com",
    "https://www.lannister-news.com",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*\.d168j68zix66ce\.amplifyapp\.com$",
    r"^https:\/\/.*\.amplifyapp\.com$",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://develop.d168j68zix66ce.amplifyapp.com",
    "https://lannister-news.com",
    "https://app.lannister-news.com",
    "https://www.lannister-news.com",
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_DOMAIN = ".lannister-news.com"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_DOMAIN = ".lannister-news.com"
print("USANDO ESTE settings.py DE LANNISTER")
"""
Django settings for lannister_news_api project.
"""

from pathlib import Path
import os
import environ


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
    # Local apps
    "users",
    "news",
    "chatbot",
]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 🔥 debe ir arriba
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lannister_news_api.urls"

# =========================
# TEMPLATES
# =========================
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
# DATABASE (MySQL - AWS RDS)
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
# CACHE / REDIS
# =========================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# =========================
# SESSIONS
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
# PASSWORD VALIDATORS
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
# STATIC
# =========================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# CUSTOM USER
# =========================
AUTH_USER_MODEL = "users.CustomUser"

...existing code...

# =========================
# MONGODB
# =========================
MONGO_DB = {
    "NAME": os.getenv("MONGO_NAME", "lannister_news"),
    "HOST": os.getenv("MONGO_HOST", "localhost"),
    "PORT": int(os.getenv("MONGO_PORT", "27017")),
    "URI": os.getenv("MONGO_URI", None),
}

# =========================
# SCRAPER CONFIG
# =========================
def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [s.strip() for s in raw.split(",") if s.strip()]

NEWS_SOURCES = _csv_env("NEWS_SOURCES")
NEWS_PROXIES = _csv_env("NEWS_PROXIES")
NEWS_USER_AGENTS = _csv_env("NEWS_USER_AGENTS")
NEWS_REQ_DELAY_MIN = float(os.getenv("NEWS_REQ_DELAY_MIN", "3"))
NEWS_REQ_DELAY_MAX = float(os.getenv("NEWS_REQ_DELAY_MAX", "8"))
NEWS_MAX_RETRIES = int(os.getenv("NEWS_MAX_RETRIES", "3"))

# =========================
# CHATBOT CONFIG
# =========================
FAQ_PATH = env("FAQ_PATH", default=os.path.join(BASE_DIR, "chatbot/faqs/faqs.json"))
FAQ_NORMALIZED_PATH = env("FAQ_NORMALIZED_PATH", default=os.path.join(BASE_DIR, "chatbot/faqs/faqs_normalized.json"))
FALLOVER_THRESHOLD = env.float("FALLOVER_THRESHOLD", default=0.08)
FALLOVER_MESSAGE = env("FALLOVER_MESSAGE", default="Lo siento, no entendí. Por favor intenta con otra pregunta.")
FAQ_MODEL_PATH = env("FAQ_MODEL_PATH", default=os.path.join(BASE_DIR, "chatbot/faq_model_2"))
