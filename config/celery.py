import os

from celery import Celery

# Устанавливаем дефолтный модуль настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически ищем задачи (tasks.py) в приложениях Django
app.autodiscover_tasks()
