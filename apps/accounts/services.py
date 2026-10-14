"""
Servicio de autenticacion y manejo de sesiones (CU-04).
Verifica hashes unidireccionales (NF-03) y emite tokens JWT con persistencia en BD.
"""
import hashlib
from datetime import timedelta
from typing import Optional, Tuple

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Estudiante, Sesion
from apps.core.exceptions import DomainException

DURACION_SESION_HORAS = 8
MENSAJE_CREDENCIALES_INVALIDAS = "Correo o contraseña incorrectos"


class AuthService:
    """Gestiona la validacion de credenciales y el ciclo de vida de la sesion."""

    @staticmethod
    def autenticar_estudiante(
        correo: str,
        contrasena_plana: str,
        ip_cliente: str = "127.0.0.1",
    ) -> Tuple[Estudiante, dict, str]:
        """
        Valida las credenciales del estudiante contra el hash almacenado y genera su sesion.
        Recibe correo, contrasena en texto plano e IP; devuelve estudiante, tokens JWT y hash.
        Lanza DomainException si las credenciales no coinciden.
        """
        if not correo or not contrasena_plana:
            raise DomainException(MENSAJE_CREDENCIALES_INVALIDAS, "AUTH_VACIO")

        correo_normalizado = correo.strip().lower()
        estudiante = Estudiante.objects.filter(correo=correo_normalizado).first()

        if not estudiante:
            raise DomainException(MENSAJE_CREDENCIALES_INVALIDAS, "AUTH_INVALIDO")

        es_contrasena_valida = check_password(contrasena_plana, estudiante.contrasena_hash)
        if not es_contrasena_valida:
            raise DomainException(MENSAJE_CREDENCIALES_INVALIDAS, "AUTH_INVALIDO")

        refresh_token = RefreshToken.for_user(estudiante)
        access_token_str = str(refresh_token.access_token)

        # Se almacena el hash SHA-256 del token para no guardar el JWT en texto plano (NF-03)
        token_hash = hashlib.sha256(access_token_str.encode("utf-8")).hexdigest()
        fecha_expiracion = timezone.now() + timedelta(hours=DURACION_SESION_HORAS)

        Sesion.objects.create(
            id_estudiante=estudiante,
            token_hash=token_hash,
            ip_acceso=ip_cliente,
            fecha_expiracion=fecha_expiracion,
        )

        tokens_jwt = {
            "access": access_token_str,
            "refresh": str(refresh_token),
        }

        return estudiante, tokens_jwt, token_hash

    @staticmethod
    def obtener_estudiante_por_sesion(request) -> Optional[Estudiante]:
        """Recupera al estudiante autenticado si su cookie de sesion es valida y no ha expirado."""
        token_hash = request.COOKIES.get("cq_session_hash")
        if not token_hash:
            return None

        sesion_activa = (
            Sesion.objects.select_related("id_estudiante")
            .filter(token_hash=token_hash, fecha_expiracion__gt=timezone.now())
            .first()
        )

        if not sesion_activa:
            return None

        return sesion_activa.id_estudiante

    @staticmethod
    def cerrar_sesion(token_hash: Optional[str]) -> None:
        """Elimina el registro de sesion activa en la base de datos."""
        if not token_hash:
            return

        Sesion.objects.filter(token_hash=token_hash).delete()

    @staticmethod
    def crear_hash_contrasena(contrasena_plana: str) -> str:
        """Genera un hash unidireccional seguro para almacenar en base de datos."""
        return make_password(contrasena_plana)
