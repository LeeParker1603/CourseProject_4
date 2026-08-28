from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Настраиваем колонки, которые будут видны в списке пользователей в админке
    list_display = ("email", "is_staff", "is_active", "email_verified", "is_blocked")

    # Фильтры в правой панели
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "email_verified",
        "is_blocked",
    )

    # Поля, по которым можно искать пользователей
    search_fields = ("email",)

    # Убираем сортировку по username, так как этого поля больше нет
    ordering = ("email",)

    # Настройка отображения полей внутри карточки пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Статусы ТЗ",
            {"fields": ("email_verified", "is_blocked", "verification_token")},
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # Поля, необходимые при создании пользователя через админку
    add_fieldsets = (
        (
            None,
            {
                "classes": ("collapse",),
                "fields": ("email", "password"),
            },
        ),
    )
