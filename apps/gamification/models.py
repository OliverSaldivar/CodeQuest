"""
Modelos de gamificacion para el registro transaccional de puntos e insignias.
Incluye el indice compuesto y la restriccion de rango definidos en el SDS v1.1.
"""
from django.db import models
from apps.accounts.models import Estudiante
from apps.challenges.models import Reto
from apps.gamification.rules import (
    RANGO_MAXIMO_VARIACION_PUNTOS,
    RANGO_MINIMO_VARIACION_PUNTOS,
)


class RegistroPuntos(models.Model):
    id_registro = models.BigAutoField(primary_key=True)
    id_estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        db_column="id_estudiante",
        related_name="registros_puntos",
    )
    id_reto = models.ForeignKey(
        Reto,
        on_delete=models.CASCADE,
        db_column="id_reto",
        related_name="registros_puntos",
    )
    variacion_puntos = models.IntegerField()
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registro_puntos"
        indexes = [
            models.Index(
                fields=["id_estudiante", "-fecha_evaluacion"],
                name="idx_reg_pts_est_fecha",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    variacion_puntos__gte=RANGO_MINIMO_VARIACION_PUNTOS,
                    variacion_puntos__lte=RANGO_MAXIMO_VARIACION_PUNTOS,
                ),
                name="chk_puntos_rango",
            )
        ]


class Insignia(models.Model):
    id_insignia = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, default="🏆")

    class Meta:
        db_table = "insignia"


class InsigniaObtenida(models.Model):
    id_insignia_obtenida = models.AutoField(primary_key=True)
    id_estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        db_column="id_estudiante",
        related_name="insignias_obtenidas",
    )
    id_insignia = models.ForeignKey(
        Insignia,
        on_delete=models.CASCADE,
        db_column="id_insignia",
    )
    fecha_obtencion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "insignia_obtenida"
        unique_together = (("id_estudiante", "id_insignia"),)
