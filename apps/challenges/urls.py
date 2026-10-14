"""Rutas para los retos de clasificacion (CU-01) y de preguntas (CU-02)."""
from django.urls import path
from apps.challenges import views

urlpatterns = [
    path(
        "retos/clasificacion/<int:id_reto>/",
        views.classification_challenge_view,
        name="classification_challenge_view",
    ),
    path(
        "retos/clasificacion/<int:id_reto>/evaluar/",
        views.evaluate_classification_api,
        name="evaluate_classification_api",
    ),
    path(
        "retos/pregunta/<int:id_reto>/",
        views.question_challenge_view,
        name="question_challenge_view",
    ),
    path(
        "retos/pregunta/<int:id_reto>/responder/",
        views.evaluate_question_api,
        name="evaluate_question_api",
    ),
]
