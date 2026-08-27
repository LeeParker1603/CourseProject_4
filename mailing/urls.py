from django.urls import path
from .views import (
    MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, ManualMailingTriggerView
)

app_name = 'mailing'

urlpatterns = [
    # Рассылки
    path('', MailingListView.as_view(), name='mailing_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),

    # Клиенты
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('mailing/<int:pk>/trigger/', ManualMailingTriggerView.as_view(), name='mailing_trigger'),
]