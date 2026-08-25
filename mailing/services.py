from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing_service(mailing):
    """Логика обработки и отправки писем для конкретной рассылки."""
    now = timezone.now()

    # 1. Проверяем, активна ли рассылка менеджером и подходит ли время
    if not mailing.is_active:
        return "Рассылка отключена администрацией."

    if not (mailing.start_time <= now <= mailing.end_time):
        return "Ошибка: Текущее время не входит в диапазон разрешенного времени отправки."

    # Обновляем статус на актуальный
    mailing.update_status()

    # 2. Получаем список клиентов
    recipients_emails = [client.email for client in mailing.recipients.all()]
    if not recipients_emails:
        return "У рассылки нет получателей."

    success_count = 0
    errors = []

    # 3. Отправка писем каждому клиенту по отдельности
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

            # Пишем лог успеха
            MailingAttempt.objects.create(
                status='Успешно',
                server_response='Письмо успешно отправлено.',
                mailing=mailing
            )
        except Exception as e:
            error_msg = str(e)
            errors.append(error_msg)

            # Пишем лог ошибки
            MailingAttempt.objects.create(
                status='Не успешно',
                server_response=f"Ошибка отправки: {error_msg}",
                mailing=mailing
            )

    return f"Отправка завершена. Успешно: {success_count}, Ошибок: {len(errors)}"