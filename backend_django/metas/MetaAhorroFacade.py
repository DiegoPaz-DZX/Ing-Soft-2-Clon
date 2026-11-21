class MetaAhorroFacade:
    def __init__(self, servicio_metas, servicio_tokens):
        self._servicio = servicio_metas
        self._tokens = servicio_tokens

    def cuenta(self, peticion):
        autorizacion = peticion.headers.get("Authorization", "")
        if not autorizacion.startswith("Bearer "):
            raise ValueError("La sesión es obligatoria.")
        return self._tokens.obtener_cuenta(autorizacion.removeprefix("Bearer ").strip())

    def listar(self, peticion):
        return self._servicio.listar(self.cuenta(peticion))

    def crear(self, peticion, datos):
        cuenta = self.cuenta(peticion)
        return self._servicio.crear(cuenta, datos.get("nombre"), datos.get("objetivo_pen"))

    def abonar(self, peticion, meta_id, datos):
        cuenta = self.cuenta(peticion)
        return self._servicio.abonar(cuenta, meta_id, datos.get("monto_pen"))

    def eliminar(self, peticion, meta_id):
        cuenta = self.cuenta(peticion)
        self._servicio.eliminar(cuenta, meta_id)

    def renombrar(self, peticion, meta_id, datos):
        cuenta = self.cuenta(peticion)
        return self._servicio.renombrar(cuenta, meta_id, datos.get("nombre"))
