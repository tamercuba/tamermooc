from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'accounts'
urlpatterns = [
    path('', views.dashboard, name='dashboard' ),
    path('entrar/', LoginView.as_view(template_name='login.html'), name='login'),
    path('sair/', LogoutView.as_view(next_page='/'), name='logout'),
    path('cadastro/', views.register, name='register'),
    path('reset-senha/', views.password_reset, name='password_reset'),
    path('nova-senha/<str:key>', views.password_reset_confirm, name='password_reset_confirm'),
    path('editar/', views.edit , name='edit'),
    path('editar-senha/', views.edit_password, name='edit_password'),
]
