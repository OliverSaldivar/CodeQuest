"""
Motor de evaluacion desacoplado (EvaluationService) para CU-01 y CU-02.
Valida clasificaciones de requerimientos, califica reactivos de opcion multiple
y registra incidencias en bitacora_error si falta el recurso teorico (Excepcion 4a CU-02).
"""
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Estudiante
from apps.analytics.models import BitacoraError
from apps.challenges.models import ClasificacionItem, Opcion, Pregunta, Reto
from apps.core.exceptions import DomainException
from apps.gamification.rules import (
    PENALIZACION_CLASIFICACION_FALLIDA,
    PENALIZACION_PREGUNTA_INCORRECTA,
    PUNTOS_PREGUNTA_CORRECTA,
    TIEMPO_LECTURA_OBLIGATORIA_SEG,
)
from apps.gamification.services import GamificationService

LEYENDA_EXPLICACION_NO_DISPONIBLE = "Explicación no disponible temporalmente"


class EvaluationService:
    """Implementa los algoritmos internos de validacion para los retos de ingenieria."""

    @staticmethod
    @transaction.atomic
    def evaluar_clasificacion_requerimientos(
        estudiante: Estudiante,
        id_reto: int,
        clasificacion_usuario: Dict[str, str],
    ) -> Dict:
        """
        Compara la ubicacion de cada requerimiento enviada por el estudiante contra la BD (CU-01).
        Si todo coincide, otorga los puntos del reto; si hay errores, devuelve la lista de IDs
        mal clasificados y aplica la penalizacion correspondiente.
        """
        reto = Reto.objects.filter(id_reto=id_reto, tipo="CLASIFICACION").first()
        if not reto:
            raise DomainException("El reto de clasificación solicitado no existe.", "RETO_404")

        items_esperados = list(ClasificacionItem.objects.filter(id_reto=reto))
        if not items_esperados:
            raise DomainException("El reto no tiene elementos configurados.", "RETO_VACIO")

        ids_incorrectos: List[int] = []
        for item in items_esperados:
            categoria_enviada = clasificacion_usuario.get(str(item.id_item))
            if categoria_enviada != item.categoria_correcta:
                ids_incorrectos.append(item.id_item)

        es_clasificacion_correcta = len(ids_incorrectos) == 0

        if not es_clasificacion_correcta:
            puntaje_actualizado = GamificationService.registrar_variacion_puntos(
                estudiante=estudiante,
                reto=reto,
                variacion_puntos=PENALIZACION_CLASIFICACION_FALLIDA,
            )
            return {
                "es_correcto": False,
                "ids_incorrectos": ids_incorrectos,
                "puntos_otorgados": PENALIZACION_CLASIFICACION_FALLIDA,
                "puntaje_total": puntaje_actualizado,
                "mensaje": (
                    f"Se detectaron {len(ids_incorrectos)} requerimiento(s) en el contenedor "
                    "equivocado. Reacomoda los elementos resaltados en rojo."
                ),
            }

        limite_recompensas = GamificationService.ha_alcanzado_limite_recompensas(
            estudiante=estudiante,
            reto=reto,
        )
        puntos_otorgados = 0 if limite_recompensas else reto.puntos_maximos

        puntaje_actualizado = GamificationService.registrar_variacion_puntos(
            estudiante=estudiante,
            reto=reto,
            variacion_puntos=reto.puntos_maximos,
        )

        mensaje_exito = (
            "¡Clasificación perfecta! Ya has completado esta actividad el máximo de 5 veces con recompensa, por lo que no se otorgan puntos adicionales."
            if limite_recompensas
            else "¡Clasificación perfecta! Has dominado la distinción entre requerimientos funcionales y no funcionales."
        )

        return {
            "es_correcto": True,
            "ids_incorrectos": [],
            "puntos_otorgados": puntos_otorgados,
            "limite_recompensas_alcanzado": limite_recompensas,
            "puntaje_total": puntaje_actualizado,
            "mensaje": mensaje_exito,
        }

    @staticmethod
    @transaction.atomic
    def evaluar_respuesta_pregunta(
        estudiante: Estudiante,
        id_reto: int,
        id_pregunta: int,
        id_opcion_seleccionada: Optional[int],
        expiro_tiempo: bool = False,
        simular_falla_teoria: bool = False,
    ) -> Dict:
        """
        Procesa la respuesta de una pregunta o su expiracion de tiempo (CU-02).
        Guarda la calificacion permanentemente y recupera la explicacion teorica.
        Si la explicacion falla o no esta disponible (Excepcion 4a), registra el incidente
        en bitacora_error sin interrumpir el avance del estudiante.
        """
        reto = Reto.objects.filter(id_reto=id_reto, tipo="PREGUNTA").first()
        if not reto:
            raise DomainException("El reto de preguntas no existe.", "RETO_404")

        pregunta = Pregunta.objects.filter(id_pregunta=id_pregunta, id_reto=reto).first()
        if not pregunta:
            raise DomainException("La pregunta solicitada no pertenece al reto.", "PREGUNTA_404")

        es_respuesta_correcta = False
        opcion_elegida = None

        if not expiro_tiempo and id_opcion_seleccionada is not None:
            opcion_elegida = Opcion.objects.filter(
                id_opcion=id_opcion_seleccionada,
                id_pregunta=pregunta,
            ).first()
            if opcion_elegida and opcion_elegida.es_correcta:
                es_respuesta_correcta = True

        limite_recompensas = (
            es_respuesta_correcta
            and GamificationService.ha_alcanzado_limite_recompensas(
                estudiante=estudiante,
                reto=reto,
            )
        )

        if es_respuesta_correcta:
            variacion_puntos = 0 if limite_recompensas else PUNTOS_PREGUNTA_CORRECTA
        else:
            variacion_puntos = PENALIZACION_PREGUNTA_INCORRECTA

        puntaje_total = GamificationService.registrar_variacion_puntos(
            estudiante=estudiante,
            reto=reto,
            variacion_puntos=PUNTOS_PREGUNTA_CORRECTA if es_respuesta_correcta else PENALIZACION_PREGUNTA_INCORRECTA,
        )

        texto_explicacion = (pregunta.explicacion_teorica or "").strip()
        fallo_carga_teoria = simular_falla_teoria or not texto_explicacion

        if fallo_carga_teoria:
            BitacoraError.objects.create(
                id_estudiante=estudiante,
                codigo="CU02_EXCEPCION_4A_TEORIA",
                mensaje="Falla al recuperar el fragmento de explicación teórica para el reactivo.",
                contexto={
                    "id_reto": reto.id_reto,
                    "id_pregunta": pregunta.id_pregunta,
                    "id_opcion_seleccionada": id_opcion_seleccionada,
                    "expiro_tiempo": expiro_tiempo,
                    "timestamp": timezone.now().isoformat(),
                },
            )
            return {
                "es_correcto": es_respuesta_correcta,
                "estado_evaluacion": "Correcto" if es_respuesta_correcta else "Incorrecto",
                "expiro_tiempo": expiro_tiempo,
                "explicacion_disponible": False,
                "explicacion_teorica": LEYENDA_EXPLICACION_NO_DISPONIBLE,
                "tiempo_espera_seg": 0,
                "puntos_otorgados": variacion_puntos,
                "puntaje_total": puntaje_total,
                "marca_tiempo": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        return {
            "es_correcto": es_respuesta_correcta,
            "estado_evaluacion": "Correcto" if es_respuesta_correcta else "Incorrecto",
            "expiro_tiempo": expiro_tiempo,
            "explicacion_disponible": True,
            "explicacion_teorica": texto_explicacion,
            "tiempo_espera_seg": TIEMPO_LECTURA_OBLIGATORIA_SEG,
            "puntos_otorgados": variacion_puntos,
            "puntaje_total": puntaje_total,
            "marca_tiempo": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
