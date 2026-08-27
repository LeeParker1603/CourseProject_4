from django.urls import path
from .views import RegisterView, UserLoginView, UserLogoutView, verify_email

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
]