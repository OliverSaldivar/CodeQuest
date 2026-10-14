"""
Controladores de vistas y endpoints para el modulo Curriculum (CU-03).
Implementa las funciones dashboard_view, skill_tree_view y get_teoria_tema
validadas en el Reporte de Pruebas TC-CU03.
"""
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from apps.accounts.services import AuthService
from apps.core.exceptions import DomainException
from apps.curriculum.services import TheoryService
from apps.gamification.models import InsigniaObtenida
from apps.gamification.services import GamificationService


@require_GET
def dashboard_view(request):
    """Redirige el acceso general del curriculum hacia la Matriz Neuronal de temas."""
    return redirect("skill_tree_view")


@require_GET
def skill_tree_view(request):
    """
    Renderiza la Matriz Neuronal (/curriculum/arbol-habilidades/) con los temas,
    retos disponibles, puntos acumulados e insignias del estudiante.
    """
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return redirect("login_view")

    temas = TheoryService.listar_temas_con_retos()
    puntaje_total = GamificationService.obtener_puntaje_total(estudiante)
    retos_completados_ids = GamificationService.obtener_retos_completados_ids(estudiante)
    insignias_usuario = InsigniaObtenida.objects.select_related("id_insignia").filter(
        id_estudiante=estudiante
    )

    contexto = {
        "estudiante": estudiante,
        "temas": temas,
        "puntaje_total": puntaje_total,
        "retos_completados_ids": retos_completados_ids,
        "insignias_usuario": insignias_usuario,
    }
    return render(request, "curriculum/skill_tree.html", contexto)


@require_GET
def get_teoria_tema(request, id_tema: int):
    """
    Endpoint REST (GET /api/teoria/<id_tema>/) para el CU-03: Consultar Teoria del Tema.
    Soporta el parametro ?simular_error=1 para probar la Excepcion 2a en vivo.
    """
    estudiante = AuthService.obtener_estudiante_por_sesion(request)
    if not estudiante:
        return JsonResponse({"error": "Sesión no válida"}, status=401)

    simular_fallo = request.GET.get("simular_error") == "1"

    try:
        datos_teoria = TheoryService.obtener_teoria_por_tema(
            id_tema=id_tema,
            simular_fallo=simular_fallo,
        )
    except DomainException as exc:
        return JsonResponse(
            {"error": exc.mensaje, "codigo": exc.codigo},
            status=503,
        )

    return JsonResponse(datos_teoria, status=200)
