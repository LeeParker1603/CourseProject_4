from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing_service(mailing):
    """Логика обработки и отправки писем с сохранением логов через batch."""
    now = timezone.now()

    if not mailing.is_active:
        return "Рассылка отключена администрацией."

    if not (mailing.start_time <= now <= mailing.end_time):
        return "Ошибка: Текущее время не входит в диапазон разрешенного времени отправки."

    mailing.update_status()

    recipients_emails = [client.email for client in mailing.recipients.all()]
    if not recipients_emails:
        return "У рассылки нет получателей."

    success_count = 0
    errors_count = 0

    # Список для batch-накопления объектов перед сохранением в БД
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

            # Вместо .create() просто добавляем объект в список (в оперативную память)
            attempts_to_create.append(
                MailingAttempt(
                    status='Успешно',
                    server_response='Письмо успешно отправлено.',
                    mailing=mailing
                )
            )
        except Exception as e:
            errors_count += 1
            attempts_to_create.append(
                MailingAttempt(
                    status='Не успешно',
                    server_response=f"Ошибка отправки: {str(e)}",
                    mailing=mailing
                )
            )

    # Выполняем БАТЧ-сохранение (один запрос в PostgreSQL вместо десятков)
    if attempts_to_create:
        MailingAttempt.objects.bulk_create(attempts_to_create)

    return f"Отправка завершена. Успешно: {success_count}, Ошибок: {errors_count}"