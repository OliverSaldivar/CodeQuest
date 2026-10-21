"""Rutas del modulo Curriculum y endpoint de teoria (CU-03)."""
from django.urls import path
from apps.curriculum import views

urlpatterns = [
    path("curriculum/", views.dashboard_view, name="dashboard_view"),
    path(
        "curriculum/arbol-habilidades/",
        views.skill_tree_view,
        name="skill_tree_view",
    ),
    path(
        "api/teoria/<int:id_tema>/",
        views.get_teoria_tema,
        name="get_teoria_tema",
    ),
]
