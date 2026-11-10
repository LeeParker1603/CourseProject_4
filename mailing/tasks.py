from celery import shared_task
from django.core.management import call_command

@shared_task
def execute_mailings():
    # Вызываем вашу существующую команду отправки рассылок
    call_command('run_mailings')