"""
Modelos del plan de estudios (Tema y Teoria) para el CU-03.
Respeta exactamente el diagrama de entidad-relacion del documento de Casos de Uso.
"""
from django.db import models


class Tema(models.Model):
    id_tema = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.CharField(max_length=40, default="⚡")
    orden = models.IntegerField(default=1)

    class Meta:
        db_table = "tema"
        ordering = ["orden"]

    def __str__(self) -> str:
        return self.nombre


class Teoria(models.Model):
    id_teoria = models.AutoField(primary_key=True)
    id_tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        db_column="id_tema",
        related_name="conceptos_teoricos",
    )
    titulo_concepto = models.CharField(max_length=150)
    contenido = models.TextField()

    class Meta:
        db_table = "teoria"

    def __str__(self) -> str:
        return f"{self.id_tema.nombre} - {self.titulo_concepto}"
