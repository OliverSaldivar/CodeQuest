"""
Enrutador principal de CodeQuest.
Redirige la raiz al flujo de inicio de sesion y conecta los modulos del MVP.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/login/", permanent=False)),
    path("", include("apps.accounts.urls")),
    path("", include("apps.curriculum.urls")),
    path("", include("apps.challenges.urls")),
]
