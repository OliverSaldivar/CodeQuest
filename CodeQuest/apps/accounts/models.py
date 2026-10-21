"""
Modelos de persistencia para la autenticacion y control de sesiones (CU-04).
Implementa el esquema DDL especificado en el SDS v1.1 con indices de busqueda rapida.
"""
from django.db import models


class Estudiante(models.Model):
    id_estudiante = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=100, unique=True, db_index=True)
    contrasena_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "estudiante"

    @property
    def is_authenticated(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"{self.nombre} ({self.correo})"


class Sesion(models.Model):
    id_sesion = models.BigAutoField(primary_key=True)
    id_estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        db_column="id_estudiante",
        related_name="sesiones",
    )
    token_hash = models.CharField(max_length=255, unique=True, db_index=True)
    ip_acceso = models.CharField(max_length=45, blank=True, null=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()

    class Meta:
        db_table = "sesion"
