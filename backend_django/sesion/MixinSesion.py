from usuarios.TokenInvalidoException import TokenInvalidoException


class MixinSesion:
    servicio_tokens = None

    def cuenta_de_la_sesion(self, peticion):
        autorizacion = peticion.headers.get("Authorization", "")
        if not autorizacion.startswith("Bearer "):
            raise TokenInvalidoException("La sesión es obligatoria.")
        return self.servicio_tokens.obtener_cuenta(autorizacion.removeprefix("Bearer ").strip())
