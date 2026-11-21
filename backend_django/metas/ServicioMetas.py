from decimal import Decimal, InvalidOperation


class ServicioMetas:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def listar(self, cuenta):
        return self._repositorio.listar(cuenta)

    def crear(self, cuenta, nombre, objetivo_pen):
        nombre = str(nombre or "").strip()
        if not nombre:
            raise ValueError("Escribe un nombre para la meta.")
        if len(nombre) > 120:                                                     # ← NUEVA
            raise ValueError("El nombre no puede superar los 120 caracteres.")
        if self._repositorio.existe_nombre(cuenta, nombre):
            raise ValueError("Ya tienes una meta con ese nombre. Elige un título diferente.")
        objetivo = self._monto_positivo(objetivo_pen, "El monto objetivo debe ser mayor que cero.")
        return self._repositorio.crear(cuenta, nombre, objetivo)

    def abonar(self, cuenta, meta_id, monto_pen):
        monto = self._monto_positivo(monto_pen, "El abono debe ser mayor que cero.")
        meta = self._repositorio.abonar(cuenta, meta_id, monto)
        if meta is None:
            raise ValueError("La meta no existe.")
        return meta

    def eliminar(self, cuenta, meta_id):
        if not self._repositorio.eliminar(cuenta, meta_id):
            raise ValueError("La meta no existe.")

    def renombrar(self, cuenta, meta_id, nombre):
        nombre = str(nombre or "").strip()
        if not nombre:
            raise ValueError("Escribe un nombre para la meta.")
        if len(nombre) > 120:
            raise ValueError("El nombre no puede superar los 120 caracteres.")

        meta = self._repositorio.obtener(cuenta, meta_id)
        if meta is None:
            raise ValueError("La meta no existe.")
        if (
            meta.nombre.casefold() != nombre.casefold()
            and self._repositorio.existe_nombre(cuenta, nombre)
        ):
            raise ValueError("Ya tienes una meta con ese nombre. Elige un título diferente.")
        return self._repositorio.actualizar_nombre(meta, nombre)

    def _monto_positivo(self, valor, mensaje):
        try:
            monto = Decimal(str(valor))
        except InvalidOperation:
            raise ValueError(mensaje)
        if not monto.is_finite() or monto <= 0:
            raise ValueError(mensaje)
        return monto