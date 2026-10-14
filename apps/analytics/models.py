"""
Modelo de auditoria y bitacora de errores (Postcondicion de error CU-02).
Utiliza JSONField (JSONB en PostgreSQL) para almacenar el contexto del incidente.
"""
from django.db import models
from apps.accounts.models import Estudiante


class BitacoraError(models.Model):
    id_error = models.BigAutoField(primary_key=True)
    id_estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_estudiante",
    )
    codigo = models.CharField(max_length=50)
    mensaje = models.TextField()
    contexto = models.JSONField(default=dict)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitacora_error"
