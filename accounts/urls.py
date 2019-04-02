from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView

app_name = 'accounts'
urlpatterns = [
    path('entrar/', LoginView.as_view(template_name='login.html'), name='login'),
]
