"""
Servicio de gamificacion encargado de registrar variaciones de puntaje,
calcular el total de experiencia y desbloquear insignias automaticamente.
"""
from django.db import transaction
from django.db.models import Sum

from apps.accounts.models import Estudiante
from apps.challenges.models import Reto
from apps.gamification.models import Insignia, InsigniaObtenida, RegistroPuntos


class GamificationService:
    """Orquesta la asignacion de puntos e insignias dentro de transacciones seguras."""

    @staticmethod
    @transaction.atomic
    def registrar_variacion_puntos(
        estudiante: Estudiante,
        reto: Reto,
        variacion_puntos: int,
    ) -> int:
        """
        Guarda un movimiento de puntos (positivo o penalizacion) y retorna el puntaje total.
        """
        RegistroPuntos.objects.create(
            id_estudiante=estudiante,
            id_reto=reto,
            variacion_puntos=variacion_puntos,
        )

        if variacion_puntos > 0:
            GamificationService._verificar_desbloqueo_insignias(estudiante, reto)

        return GamificationService.obtener_puntaje_total(estudiante)

    @staticmethod
    def obtener_puntaje_total(estudiante: Estudiante) -> int:
        """Calcula la suma acumulada de puntos del estudiante sin bajar de cero."""
        resultado = RegistroPuntos.objects.filter(id_estudiante=estudiante).aggregate(
            total=Sum("variacion_puntos")
        )
        puntaje_bruto = resultado["total"] or 0
        return max(0, puntaje_bruto)

    @staticmethod
    def obtener_retos_completados_ids(estudiante: Estudiante) -> set:
        """Devuelve el conjunto de IDs de retos donde el estudiante obtuvo puntaje positivo."""
        ids = (
            RegistroPuntos.objects.filter(
                id_estudiante=estudiante,
                variacion_puntos__gt=0,
            )
            .values_list("id_reto_id", flat=True)
            .distinct()
        )
        return set(ids)

    @staticmethod
    def _verificar_desbloqueo_insignias(estudiante: Estudiante, reto: Reto) -> None:
        """Otorga insignias segun el tipo de reto superado."""
        codigo_insignia = (
            "ARQUITECTO_REQ" if reto.tipo == "CLASIFICACION" else "MENTE_ANALITICA"
        )
        insignia = Insignia.objects.filter(codigo=codigo_insignia).first()
        if not insignia:
            return

        InsigniaObtenida.objects.get_or_create(
            id_estudiante=estudiante,
            id_insignia=insignia,
        )
