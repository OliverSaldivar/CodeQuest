"""Excepciones personalizadas de dominio para desacoplar errores de negocio de la capa HTTP."""


class DomainException(Exception):
    """Excepcion base para errores controlados en la capa de servicios."""

    def __init__(self, mensaje: str, codigo: str = "ERROR_DOMINIO"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
