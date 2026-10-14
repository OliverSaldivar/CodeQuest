"""
Modelos de datos para los retos interactivos de clasificacion (CU-01) y preguntas (CU-02).
Implementa las restricciones CHECK y UNIQUE compuestas definidas en el SDS v1.1.
"""
from django.db import models
from apps.curriculum.models import Tema


class Reto(models.Model):
    TIPOS_RETO = [
        ("CLASIFICACION", "Clasificación de Requerimientos"),
        ("PREGUNTA", "Preguntas de Opción Múltiple"),
    ]

    id_reto = models.AutoField(primary_key=True)
    id_tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        db_column="id_tema",
        related_name="retos",
    )
    tipo = models.CharField(max_length=20, choices=TIPOS_RETO)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    puntos_maximos = models.IntegerField(default=100)
    orden = models.IntegerField(default=1)

    class Meta:
        db_table = "reto"
        ordering = ["orden"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(tipo__in=["CLASIFICACION", "PREGUNTA"]),
                name="chk_reto_tipo_valido",
            )
        ]


class ClasificacionItem(models.Model):
    CATEGORIAS_REQUERIMIENTO = [
        ("FUNCIONAL", "Requerimiento Funcional"),
        ("NO_FUNCIONAL", "Requerimiento No Funcional"),
    ]

    id_item = models.AutoField(primary_key=True)
    id_reto = models.ForeignKey(
        Reto,
        on_delete=models.CASCADE,
        db_column="id_reto",
        related_name="items_clasificacion",
    )
    descripcion = models.TextField()
    categoria_correcta = models.CharField(max_length=20, choices=CATEGORIAS_REQUERIMIENTO)
    orden = models.IntegerField(default=1)

    class Meta:
        db_table = "clasificacion_item"
        ordering = ["orden"]


class Pregunta(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    id_reto = models.ForeignKey(
        Reto,
        on_delete=models.CASCADE,
        db_column="id_reto",
        related_name="preguntas",
        db_index=True,
    )
    enunciado = models.TextField()
    explicacion_teorica = models.TextField(blank=True, null=True)
    tiempo_limite_seg = models.IntegerField(default=30)
    orden = models.IntegerField(default=1)

    class Meta:
        db_table = "pregunta"
        ordering = ["orden"]


class Opcion(models.Model):
    id_opcion = models.AutoField(primary_key=True)
    id_pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        db_column="id_pregunta",
        related_name="opciones",
    )
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    orden = models.IntegerField(default=1)

    class Meta:
        db_table = "opcion"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["id_pregunta", "orden"],
                name="uq_opcion_pregunta",
            )
        ]
