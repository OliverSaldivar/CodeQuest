"""
Servicio de consulta del plan de estudios y conceptos teoricos (CU-03).
"""
from typing import Dict, List
from django.db import DatabaseError

from apps.core.exceptions import DomainException
from apps.curriculum.models import Tema, Teoria

MENSAJE_TEORIA_NO_DISPONIBLE = "Contenido no disponible temporalmente"


class TheoryService:
    """Provee acceso desacoplado a los temas y sus fragmentos teoricos."""

    @staticmethod
    def obtener_teoria_por_tema(id_tema: int, simular_fallo: bool = False) -> Dict:
        """
        Consulta los conceptos teoricos asociados a un tema especifico (CU-03).
        Lanza DomainException con el mensaje 'Contenido no disponible temporalmente'
        si el tema no tiene teoria o si ocurre una falla de conexion (Excepcion 2a).
        """
        if simular_fallo:
            raise DomainException(MENSAJE_TEORIA_NO_DISPONIBLE, "DB_TIMEOUT_SIMULADO")

        try:
            tema = Tema.objects.filter(id_tema=id_tema).first()
            if not tema:
                raise DomainException(MENSAJE_TEORIA_NO_DISPONIBLE, "TEMA_NO_ENCONTRADO")

            lista_conceptos = list(
                Teoria.objects.filter(id_tema=tema).values(
                    "id_teoria",
                    "titulo_concepto",
                    "contenido",
                )
            )
        except DatabaseError as exc:
            raise DomainException(MENSAJE_TEORIA_NO_DISPONIBLE, "DB_ERROR") from exc

        if not lista_conceptos:
            raise DomainException(MENSAJE_TEORIA_NO_DISPONIBLE, "SIN_TEORIA")

        return {
            "id_tema": tema.id_tema,
            "nombre_tema": tema.nombre,
            "descripcion_tema": tema.descripcion,
            "conceptos": lista_conceptos,
        }

    @staticmethod
    def listar_temas_con_retos() -> List[Tema]:
        """Recupera todos los temas del plan de estudios junto con sus retos asociados."""
        return list(Tema.objects.prefetch_related("retos").all())
