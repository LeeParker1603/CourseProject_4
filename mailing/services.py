from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import MailingAttempt


def send_mailing_service(mailing):
    """Логика обработки и отправки писем без привязки к часовым поясам."""
    # При USE_TZ=False этот метод выдаст чистое локальное время компьютера
    current_time = timezone.now()

    if not mailing.is_active:
        return "Рассылка отключена администрацией."

    # Проверка диапазона времени
    if not (mailing.start_time <= current_time <= mailing.end_time):
        return f"Ошибка: Текущее время {current_time.strftime('%H:%M')} не входит в диапазон разрешенного времени отправки."

    mailing.update_status()

    recipients_emails = [client.email for client in mailing.recipients.all()]
    if not recipients_emails:
        return "У рассылки нет получателей."

    success_count = 0
    errors_count = 0
    attempts_to_create = []

    for client_email in recipients_emails:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                fail_silently=False,
            )
            success_count += 1
            attempts_to_create.append(
                MailingAttempt(
                    status="Успешно",
                    server_response="Письмо успешно отправлено.",
                    mailing=mailing,
                )
            )
        except Exception as e:
            errors_count += 1
            attempts_to_create.append(
                MailingAttempt(
                    status="Не успешно",
                    server_response=f"Ошибка отправки: {str(e)}",
                    mailing=mailing,
                )
            )

    if attempts_to_create:
        MailingAttempt.objects.bulk_create(attempts_to_create)

    return f"Отправка завершена. Успешно: {success_count}, Ошибок: {errors_count}"
