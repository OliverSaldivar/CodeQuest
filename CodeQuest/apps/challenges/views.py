"""
Vistas y endpoints REST para la resolucion de retos de clasificacion (CU-01)
y preguntas con retroalimentacion inmediata (CU-02).
"""
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.accounts.services import AuthService
from apps.challenges.models import Reto
from apps.challenges.services import EvaluationService
from apps.core.exceptions import DomainException
from apps.gamification.rules import (
    MAX_INTENTOS_CLASIFICACION,
    TIEMPO_LECTURA_OBLIGATORIA_SEG,
)
from apps.gamification.services import GamificationService


@require_GET
def classification_challenge_view(request, id_reto: int):
    """Renderiza el escenario interactivo Drag & Drop para clasificar requerimientos (CU-01)."""
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return redirect("login_view")

    reto = get_object_or_404(Reto, id_reto=id_reto, tipo="CLASIFICACION")
    items = reto.items_clasificacion.all()
    puntaje_total = GamificationService.obtener_puntaje_total(estudiante)

    contexto = {
        "estudiante": estudiante,
        "reto": reto,
        "items": items,
        "max_intentos": MAX_INTENTOS_CLASIFICACION,
        "puntaje_total": puntaje_total,
    }
    return render(request, "challenges/classification.html", contexto)


@csrf_exempt
@require_POST
def evaluate_classification_api(request, id_reto: int):
    """Endpoint POST (/retos/clasificacion/<id_reto>/evaluar/) invocado en el CU-01."""
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return JsonResponse({"error": "Sesión expirada"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        clasificacion_usuario = payload.get("clasificacion", {})
        resultado = EvaluationService.evaluar_clasificacion_requerimientos(
            estudiante=estudiante,
            id_reto=id_reto,
            clasificacion_usuario=clasificacion_usuario,
        )
    except DomainException as exc:
        return JsonResponse({"error": exc.mensaje}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Payload JSON inválido"}, status=400)

    return JsonResponse(resultado, status=200)


@require_GET
def question_challenge_view(request, id_reto: int):
    """Renderiza el reto de preguntas secuenciales con temporizador y modal teorico (CU-02)."""
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return redirect("login_view")

    reto = get_object_or_404(Reto, id_reto=id_reto, tipo="PREGUNTA")
    preguntas_qs = reto.preguntas.prefetch_related("opciones").all()

    lista_preguntas = []
    for pregunta in preguntas_qs:
        lista_preguntas.append(
            {
                "id_pregunta": pregunta.id_pregunta,
                "enunciado": pregunta.enunciado,
                "tiempo_limite_seg": pregunta.tiempo_limite_seg,
                "orden": pregunta.orden,
                "opciones": [
                    {
                        "id_opcion": op.id_opcion,
                        "texto": op.texto,
                        "orden": op.orden,
                    }
                    for op in pregunta.opciones.all()
                ],
            }
        )

    puntaje_total = GamificationService.obtener_puntaje_total(estudiante)
    contexto = {
        "estudiante": estudiante,
        "reto": reto,
        "preguntas_json": json.dumps(lista_preguntas),
        "tiempo_lectura_seg": TIEMPO_LECTURA_OBLIGATORIA_SEG,
        "puntaje_total": puntaje_total,
    }
    return render(request, "challenges/question.html", contexto)


@csrf_exempt
@require_POST
def evaluate_question_api(request, id_reto: int):
    """Endpoint POST (/retos/pregunta/<id_reto>/responder/) para calificar una pregunta (CU-02)."""
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return JsonResponse({"error": "Sesión expirada"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        id_pregunta = int(payload.get("id_pregunta", 0))
        id_opcion = payload.get("id_opcion")
        id_opcion_int = int(id_opcion) if id_opcion is not None else None
        expiro_tiempo = bool(payload.get("expiro_tiempo", False))
        simular_falla_teoria = bool(payload.get("simular_falla_teoria", False))

        resultado = EvaluationService.evaluar_respuesta_pregunta(
            estudiante=estudiante,
            id_reto=id_reto,
            id_pregunta=id_pregunta,
            id_opcion_seleccionada=id_opcion_int,
            expiro_tiempo=expiro_tiempo,
            simular_falla_teoria=simular_falla_teoria,
        )
    except (DomainException, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Payload JSON inválido"}, status=400)

    return JsonResponse(resultado, status=200)
