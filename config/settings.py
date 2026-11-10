import os
import sys
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

# 1. ГЛОБАЛЬНЫЙ ПАТЧ: Отключаем RESP3/HELLO и уведомления об обслуживании для старого Redis на Windows
from redis.connection import Connection

# Отключаем проверку уведомлений об обслуживании, которая вызывает RedisError
Connection._configure_maintenance_notifications = lambda *args, **kwargs: None

# Перехватываем инициализацию соединения и принудительно задаем протокол RESP2
original_init = Connection.__init__


def patched_init(self, *args, **kwargs):
    kwargs["protocol"] = 2  # Блокирует команду HELLO
    original_init(self, *args, **kwargs)


Connection.__init__ = patched_init

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из .env
load_dotenv(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Наши приложения
    "mailing.apps.MailingConfig",
    "users.apps.UsersConfig",
]


# Указываем Django использовать нашу кастомную модель пользователя (подготовим её сразу)
AUTH_USER_MODEL = "users.User"


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


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "OPTIONS": {
            "client_encoding": "UTF8",  # Принудительно устанавливаем UTF-8 для клиента
        },
    }
}

# Если запущен скрипт тестирования, подменяем БД на встроенную SQLite
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": os.getenv("EMAIL_HOST"),
            "port": (
                int(os.getenv("EMAIL_PORT", 465)) if os.getenv("EMAIL_PORT") else 465
            ),
            "username": os.getenv("EMAIL_HOST_USER"),
            "password": os.getenv("EMAIL_HOST_PASSWORD"),
            "use_ssl": os.getenv("EMAIL_USE_SSL") == "True",
        },
    }
}

# От чьего имени отправляются письма по умолчанию
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Куда перенаправлять после успешного входа
LOGIN_REDIRECT_URL = "mailing:mailing_list"
# Куда перенаправлять после выхода из аккаунта
LOGOUT_REDIRECT_URL = "users:login"
# Страница, куда перекинет пользователя, если он не авторизован, но пытается зайти на закрытую страницу
LOGIN_URL = "users:login"

SESSION_COOKIE_AGE = 1209600  # 2 недели сессии
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}


# Настройки Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Настройка периодической задачи

CELERY_BEAT_SCHEDULE = {
    "run_mailings_every_5_minutes": {
        "task": "mailing.tasks.execute_mailings",
        "schedule": crontab(minute="*/5"),  # Каждые 5 минут
    },
}

csrf_trusted = os.getenv('CSRF_TRUSTED_ORIGINS')
if csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted.split(',')]
