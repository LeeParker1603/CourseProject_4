from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import send_mailing_service


class Command(BaseCommand):
    help = (
        "Автоматический фоновый запуск всех актуальных рассылок по локальному времени"
    )

    def handle(self, *args, **kwargs):
        # Берем текущее чистое время компьютера
        current_time = timezone.now()

        active_mailings = Mailing.objects.filter(
            is_active=True, start_time__lte=current_time, end_time__gte=current_time
        )

        if not active_mailings.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Нет подходящих рассылок для времени {current_time.strftime("%H:%M")}.'
                )
            )
            return

        for mailing in active_mailings:
            self.stdout.write(f"Запуск рассылки ID {mailing.id}...")
            result = send_mailing_service(mailing)
            self.stdout.write(
                self.style.SUCCESS(f"Результат для ID {mailing.id}: {result}")
            )
