"""
Controladores de presentacion y API para el inicio de sesion (CU-04).
Delega toda la logica de negocio a AuthService.
"""
import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.accounts.services import DURACION_SESION_HORAS, AuthService
from apps.core.exceptions import DomainException

SEGUNDOS_POR_HORA = 3600


@require_GET
def login_view(request):
    """
    Renderiza el formulario de login o redirige a la pantalla principal
    si el estudiante ya cuenta con una sesion activa (Flujo alternativo CU-04).
    """
    estudiante_activo = AuthService.obtener_estudiante_por_sesion(request)
    if estudiante_activo:
        return redirect("skill_tree_view")

    return render(request, "accounts/login.html")


@csrf_exempt
@require_POST
def api_login_view(request):
    """
    Endpoint REST (/api/accounts/login/) para autenticar credenciales y emitir tokens JWT.
    """
    try:
        datos_entrada = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON inválido"}, status=400)

    correo = datos_entrada.get("correo", "")
    contrasena = datos_entrada.get("password", "")
    ip_cliente = request.META.get("REMOTE_ADDR", "127.0.0.1")

    try:
        estudiante, tokens_jwt, token_hash = AuthService.autenticar_estudiante(
            correo=correo,
            contrasena_plana=contrasena,
            ip_cliente=ip_cliente,
        )
    except DomainException as exc:
        return JsonResponse({"error": exc.mensaje, "codigo": exc.codigo}, status=401)

    respuesta = JsonResponse(
        {
            "mensaje": "Autenticación exitosa",
            "estudiante": {
                "id_estudiante": estudiante.id_estudiante,
                "nombre": estudiante.nombre,
                "correo": estudiante.correo,
            },
            "access": tokens_jwt["access"],
            "refresh": tokens_jwt["refresh"],
            "redirect_url": "/curriculum/arbol-habilidades/",
        },
        status=200,
    )

    tiempo_vida_cookie_seg = DURACION_SESION_HORAS * SEGUNDOS_POR_HORA
    respuesta.set_cookie(
        "cq_session_hash",
        token_hash,
        max_age=tiempo_vida_cookie_seg,
        httponly=True,
        samesite="Lax",
    )

    return respuesta


@require_GET
def logout_view(request):
    """Finaliza la sesion activa del estudiante y redirige al login."""
    token_hash = request.COOKIES.get("cq_session_hash")
    AuthService.cerrar_sesion(token_hash)

    respuesta = redirect("login_view")
    respuesta.delete_cookie("cq_session_hash")
    return respuesta
