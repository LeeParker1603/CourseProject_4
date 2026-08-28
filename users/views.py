import secrets

from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import UserLoginForm, UserRegisterForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Блокируем аккаунт до подтверждения почты

        # Генерируем уникальный токен
        token = secrets.token_hex(16)
        user.verification_token = token
        user.save()

        # Формируем ссылку для отправки на email
        host = self.request.get_host()
        url = f"http://{host}{reverse('users:verify_email', kwargs={'token': token})}"

        # Отправляем письмо через манеру новых версий MAILERS
        send_mail(
            subject="Подтверждение регистрации на сервисе Рассылок",
            message=f"Для подтверждения вашей учетной записи перейдите по ссылке: {url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return render(self.request, "users/verify_message.html")


def verify_email(request, token):
    """Контроллер, активирующий пользователя при переходе по ссылке из письма."""
    user = get_object_or_404(User, verification_token=token)
    user.is_active = True
    user.email_verified = True
    user.verification_token = None  # Стираем одноразовый токен
    user.save()
    return render(request, "users/verify_success.html")


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"


class UserLogoutView(LogoutView):
    pass
