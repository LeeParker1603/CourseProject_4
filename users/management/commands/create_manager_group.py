from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическое создание группы "Менеджеры" с необходимыми правами доступа по ТЗ'

    def handle(self, *args, **kwargs):
        # 1. Создаем или получаем группу 'Менеджеры'
        group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана!'))
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Менеджеры" уже существует в базе данных.')
            )

        # 2. Собираем права доступа согласно требованиям ТЗ
        permissions_to_add = []

        # Права для управления Рассылками (Mailing): только просмотр (view) и изменение (change для отключения)
        mailing_ct = ContentType.objects.get_for_model(Mailing)
        permissions_to_add.append(
            Permission.objects.get(codename="view_mailing", content_type=mailing_ct)
        )
        permissions_to_add.append(
            Permission.objects.get(codename="change_mailing", content_type=mailing_ct)
        )

        # Права для просмотра списка Клиентов (Client)
        client_ct = ContentType.objects.get_for_model(Client)
        permissions_to_add.append(
            Permission.objects.get(codename="view_client", content_type=client_ct)
        )

        # Права для просмотра и блокировки Пользователей (User)
        user_ct = ContentType.objects.get_for_model(User)
        permissions_to_add.append(
            Permission.objects.get(codename="view_user", content_type=user_ct)
        )
        permissions_to_add.append(
            Permission.objects.get(codename="change_user", content_type=user_ct)
        )

        # 3. Назначаем права группе (используем set() для перезаписи или .add() для добавления)
        group.permissions.set(permissions_to_add)

        self.stdout.write(
            self.style.SUCCESS(
                'Все необходимые права доступа успешно привязаны к группе "Менеджеры"!'
            )
        )
