from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None  # убираем username, вход будет по email
    email = models.EmailField(unique=True, verbose_name='Email')

    # Дополнительные поля по ТЗ (Часть 2)
    email_verified = models.BooleanField(default=False, verbose_name='Email подтвержден')
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

