from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User, где email является уникальным идентификатором."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email должен быть указан")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Суперпользователь активен сразу

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Полностью удаляем поле username
    email = models.EmailField(unique=True, verbose_name="Email")

    # Дополнительные поля по ТЗ
    email_verified = models.BooleanField(
        default=False, verbose_name="Email подтвержден"
    )
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    # Указываем Django использовать наш новый менеджер
    objects = UserManager()

    USERNAME_FIELD = "email"  # Поле для входа в систему
    REQUIRED_FIELDS = []  # при создании (username не попросит)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
