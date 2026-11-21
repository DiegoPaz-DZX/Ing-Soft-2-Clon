from usuarios.TokenInvalidoException import TokenInvalidoException


def obtener_token(peticion):
    autorizacion = peticion.headers.get("Authorization", "")
    if not autorizacion.startswith("Bearer "):
        raise TokenInvalidoException("La sesión es obligatoria.")
    return autorizacion.removeprefix("Bearer ").strip()
