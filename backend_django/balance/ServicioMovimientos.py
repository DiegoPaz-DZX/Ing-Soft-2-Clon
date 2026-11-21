from datetime import date
from decimal import Decimal, InvalidOperation
import os

from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .MontoInvalidoException import MontoInvalidoException
from .Movimiento import Movimiento
from .MovimientoNoEncontradoException import MovimientoNoEncontradoException
from .MovimientoConValidacion import MovimientoConValidacion
from .TipoMovimiento import TipoMovimiento
from .ValidadorEdicionMovimiento import ValidadorEdicionMovimiento

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".jfif", ".png", ".pdf"}
TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "application/pdf"}
TAMANO_MAXIMO_MB = 5
MONEDAS_PERMITIDAS = {"PEN", "USD"}  # NUEVO


class ServicioMovimientos:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    # NUEVO: parámetro "moneda" al final
    def registrar_movimiento(
        self, cuenta, tipo, monto, fecha, descripcion="", comprobante=None, categoria="", moneda="PEN",
        meta_id=None
    ):
        movimiento = self.preparar_movimiento(
            cuenta, tipo, monto, fecha, descripcion, comprobante, categoria, moneda, meta_id
        )
        self._repositorio.agregar(movimiento)
        return movimiento

    def preparar_movimiento(
        self, cuenta, tipo, monto, fecha, descripcion="", comprobante=None, categoria="", moneda="PEN",
        meta_id=None
    ):
        if comprobante:
            self._validar_comprobante(comprobante)
        tipo_valido = self._convertir_tipo(tipo)
        meta = self._obtener_meta(cuenta, meta_id, tipo_valido, categoria)
        return Movimiento(
            usuario = cuenta,
            tipo=tipo_valido,
            monto=self._convertir_monto(monto),
            moneda=self._convertir_moneda(moneda),  # NUEVO
            fecha=self._convertir_fecha(fecha),
            descripcion=(descripcion or "").strip(),
            categoria=(categoria or "").strip().lower() if tipo_valido == TipoMovimiento.GASTO else "",
            comprobante=comprobante or None,
            meta=meta,
        )

    def eliminar_movimiento(self, cuenta, movimiento_id):
        eliminado = self._repositorio.eliminar(cuenta, movimiento_id)
        if not eliminado:
            raise MovimientoNoEncontradoException(
                'El movimiento no existe o no pertenece a esta cuenta.'
            )

    # NUEVO (HU18): edita un movimiento existente
    def editar_movimiento(
        self, cuenta, movimiento_id, tipo, monto, fecha, descripcion="", categoria="", moneda="PEN",
        meta_id=None
    ):
        movimiento = self._repositorio.obtener_por_id(cuenta, movimiento_id)
        if movimiento is None:
            raise MovimientoNoEncontradoException("El movimiento no existe")

        movimiento.tipo = self._convertir_tipo(tipo)
        movimiento.monto = self._convertir_monto(monto)
        movimiento.fecha = self._convertir_fecha(fecha)
        movimiento.descripcion = (descripcion or "").strip()
        movimiento.moneda = self._convertir_moneda(moneda)
        movimiento.categoria = (
            (categoria or "").strip().lower() if movimiento.tipo == TipoMovimiento.GASTO else ""
        )
        movimiento.meta = self._obtener_meta(cuenta, meta_id, movimiento.tipo, movimiento.categoria)
        
        # Decorator Pattern: envuelve el movimiento con validación antes de guardar
        movimiento_validado = MovimientoConValidacion(movimiento)
        movimiento_validado.validar()
        
        return self._repositorio.actualizar(movimiento)

    def _obtener_meta(self, cuenta, meta_id, tipo, categoria):
        if not meta_id:
            if tipo == TipoMovimiento.GASTO and categoria == "ahorro":
                raise DatosMovimientoInvalidosException(
                    "Selecciona la meta que recibirá este ahorro."
                )
            return None
        if tipo != TipoMovimiento.GASTO or categoria != "ahorro":
            raise DatosMovimientoInvalidosException(
                "La meta solo puede asociarse a un gasto de categoría ahorro."
            )
        meta = self._repositorio.obtener_meta(cuenta, meta_id)
        if meta is None:
            raise DatosMovimientoInvalidosException("La meta no existe o no pertenece a esta cuenta.")
        return meta

    def _convertir_moneda(self, moneda):
        valor = str(moneda or "PEN").strip().upper()
        if valor not in MONEDAS_PERMITIDAS:
            raise DatosMovimientoInvalidosException("La moneda debe ser Soles (PEN) o Dólares (USD)")
        return valor

    def _validar_comprobante(self, archivo):
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS or archivo.content_type not in TIPOS_PERMITIDOS:
            raise DatosMovimientoInvalidosException("Solo se permiten archivos JPG, PNG o PDF")
        if archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024:
            raise DatosMovimientoInvalidosException(
                f"El archivo no puede superar los {TAMANO_MAXIMO_MB} MB"
            )

    def _convertir_tipo(self, tipo):
        valor = str(tipo or "").upper()
        if valor not in TipoMovimiento.values:
            raise DatosMovimientoInvalidosException("El tipo debe ser ingreso o gasto")
        return valor

    def _convertir_monto(self, monto):
        try:
            valor = Decimal(str(monto))
        except InvalidOperation:
            raise MontoInvalidoException("El monto debe ser un número")
        if not valor.is_finite() or valor <= 0:
            raise MontoInvalidoException("El monto debe ser mayor que cero")
        return valor

    def _convertir_fecha(self, fecha):
        try:
            return date.fromisoformat(str(fecha))
        except ValueError:
            raise DatosMovimientoInvalidosException("La fecha es obligatoria (AAAA-MM-DD)")
