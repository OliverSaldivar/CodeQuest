"""Rutas de autenticacion y sesion (CU-04)."""
from django.urls import path
from apps.accounts import views

urlpatterns = [
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("api/accounts/login/", views.api_login_view, name="api_login_view"),
]
