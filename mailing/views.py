from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Mailing, Client, Message
from .forms import MailingForm, ClientForm, MessageForm

# ==========================================
# КОНТРОЛЛЕРЫ ДЛЯ УПРАВЛЕНИЯ РАССЫЛКАМИ
# ==========================================

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        # Пользователь видит только свои рассылки, менеджер — все (Часть 2 ТЗ)
        if self.request.user.groups.filter(name='Менеджеры').exists() or self.request.user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        """Вызывается при открытии страницы рассылки. Пересчитывает её статус."""
        obj = super().get_object(queryset)
        obj.update_status()  # Вызов динамического пересчета и сохранения из модели
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        # Передаем текущего пользователя в форму, чтобы отфильтровать его клиентов и сообщения
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Автоматически назначаем текущего пользователя владельцем рассылки
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        # Редактировать может только владелец (менеджерам чужое нельзя по ТЗ)
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_superuser


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        # Удалять может только владелец
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_superuser


# ==========================================
# КОНТРОЛЛЕРЫ ДЛЯ УПРАВЛЕНИЯ КЛИЕНТАМИ (ПОЛУЧАТЕЛЯМИ)
# ==========================================

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists() or self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser

class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser
